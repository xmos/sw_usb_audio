import io
import os
from pathlib import Path
import pytest
import sh
import stat
import time
import re
import requests
from typing import List
import xtagctl

XMOS_ROOT = Path(os.environ["XMOS_ROOT"])

XSIG_LINUX_URL = "http://intranet/projects/usb_audio_regression_files/xsig/linux/xsig"
XSIG_PATH = Path(__file__).parent / "xsig"
XSIG_CONFIG_ROOT = XMOS_ROOT / "usb_audio_testing/xsig_configs"


def get_firmware_path_harness(board, config=None):
    if config is None:
        return (
            XMOS_ROOT
            / "sw_audio_analyzer"
            / f"app_audio_analyzer_{board}"
            / "bin"
            / f"app_audio_analyzer_{board}.xe"
        )
    else:
        return (
            XMOS_ROOT
            / "sw_audio_analyzer"
            / f"app_audio_analyzer_{board}"
            / "bin"
            / f"{config}"
            / f"app_audio_analyzer_{board}_{config}.xe"
        )


def get_firmware_path(board, config):
    firmware_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.xe"
    )
    return firmware_path


def get_target_file(board):
    target_file_dir = (
        XMOS_ROOT / "sw_usb_audio" / f"app_usb_aud_{board}" / "src" / f"core"
    )
    for p in target_file_dir.iterdir():
        if p.is_file() and p.suffix == ".xn":
            return p
    return None


@pytest.fixture
def xsig():
    r = requests.get(XSIG_LINUX_URL)
    with open(XSIG_PATH, "wb") as f:
        f.write(r.content)

    XSIG_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    return XSIG_PATH


def check_analyzer_output(analyzer_output: List[str], expected_frequencies: int):
    """ Verify that the output from xsig is correct """

    failures = []
    # Check for any errors
    for line in analyzer_output:
        if re.match(".*ERROR|.*error|.*Error|.*Problem", line):
            failures.append(line)

    # Check that the signals detected are of the correct frequencies
    for i, expected_freq in enumerate(expected_frequencies):
        found = False
        expected_freq = expected_frequencies[i]
        expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
        for line in analyzer_output:
            if line.startswith(expected_line):
                found = True
        if not found:
            failures.append(
                "Expected frequency of %d not seen on channel %d" % (expected_freq, i)
            )

    for line in analyzer_output:
        # Check that the signals were never lost
        if re.match("Channel [0-9]*: Lost signal", line):
            failures.append(line)
        # Check that unexpected signals are not detected
        if re.match("Channel [0-9]*: Signal detected .*", line):
            chan_num = int(re.findall(r"\d", line)[0])
            if chan_num not in range(len(expected_frequencies)):
                failures.append("Unexpected signal detected on channel %d" % chan_num)
        if re.match("Channel [0-9]*: Frequency [0-9]* .*", line):
            chan_num = int(re.findall(r"\d", line)[0])
            if chan_num not in range(len(expected_frequencies)):
                failures.append(
                    "Unexpected frequency reported on channel %d" % chan_num
                )

    if len(failures) > 0:
        print("\n".join(failures))
        return False
    return True


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_input_8ch.json"])
@pytest.mark.parametrize("board_and_config", [("xk_216_mc", "2i8o8xxxxx_tdm8")])
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_input(
    xsig, fs, duration_ms, xsig_config, board_and_config, num_chans
):
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_id:
        # xflash the firmware
        board, config = board_and_config
        firmware = get_firmware_path(board, config)
        sh.xrun("--adapter-id", adapter_id, firmware)
        # Wait for device to enumerate
        time.sleep(10)
        # Run xsig
        xsig_output = sh.Command(xsig)(fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config)
        xsig_lines = xsig_output.split("\n")
        # Check output
        expected_freqs = [(i+1) * 1000 for i in range(num_chans)]
        assert check_analyzer_output(xsig_lines, expected_freqs)


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_output.json"])
@pytest.mark.parametrize("board_and_config", [("xk_216_mc", "2i8o8xxxxx_tdm8")])
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_output(
    xsig, fs, duration_ms, xsig_config, board_and_config, num_chans
):
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_dut:
        with xtagctl.target("usb_audio_mc_xs2_harness") as adapter_harness:
            print(f"Adapter DUT: {adapter_dut}, Adapter harness: {adapter_harness}")
            # xrun the dut
            board, config = board_and_config
            firmware = get_firmware_path(board, config)
            sh.xrun("--adapter-id", adapter_dut, firmware)
            # xrun --xscope the harness
            harness_firmware = get_firmware_path_harness("xcore200_mc")
            xscope_out = io.StringIO()
            harness_xrun = sh.xrun(
                "--adapter-id",
                adapter_harness,
                "--xscope",
                harness_firmware,
                _out=xscope_out,
                _err_to_out=True,
                _bg=True,
                _bg_exc=False
            )
            # Wait for device(s) to enumerate
            time.sleep(10)
            # Run xsig
            xsig_output = sh.Command(xsig)(
                fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config
            )
            xsig_lines = xsig_output.split("\n")
            # Check analyzer output
            try:
                harness_xrun.kill_group()
                harness_xrun.wait()
            except sh.SignalException:
                # Killed
                pass

            xscope_str = xscope_out.getvalue()
            xscope_lines = xscope_str.split("\n")
            print("XSCOPE STRING:")
            print(xscope_str)
            expected_freqs = [((i+1) * 1000) + 500 for i in range(num_chans)]
            assert check_analyzer_output(xscope_lines, expected_freqs)


if __name__ == "__main__":
    test_analogue_output(
        Path("./xsig").resolve(),
        48000,
        10000,
        "mc_analogue_output.json",
        ("xk_216_mc", "2i8o8xxxxx_tdm8"),
        8,
    )
