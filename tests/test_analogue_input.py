import os
from pathlib import Path
import pytest
import sh
import stat
import time
import re
import requests
from typing import List

XMOS_ROOT = Path(os.environ["XMOS_ROOT"])

XSIG_LINUX_URL = "http://intranet/projects/usb_audio_regression_files/xsig/linux/xsig"
XSIG_PATH = Path(__file__).parent / "xsig"
XSIG_CONFIG_ROOT = XMOS_ROOT / "usb_audio_testing/xsig_configs"


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
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "src"
        / f"core"
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


def check_xsig_output(xsig_output: List[str], num_chans: int):
    """ Verify that the output from xsig is correct """

    failures = []
    # Check for any errors
    for line in xsig_output:
        if re.match(".*ERROR|.*error|.*Error|.*Problem", line):
            failures.append(line)

    # Check that the signals detected are of the correct frequencies
    for i in range(num_chans):
        found = False
        expected_freq = (i + 1) * 1000
        expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
        for line in xsig_output:
            if line.startswith(expected_line):
                found = True
        if not found:
            failures.append(
                "Expected frequency of %d not seen on channel %d" % (expected_freq, i)
            )

    for line in xsig_output:
        # Check that the signals were never lost
        if re.match("Channel [0-9]*: Lost signal", line):
            failures.append(line)
        # Check that unexpected signals are not detected
        if re.match("Channel [0-9]*: Signal detected .*", line):
            chan_num = int(re.findall(r"\d", line)[0])
            if chan_num not in range(num_chans):
                failures.append("Unexpected signal detected on channel %d" % chan_num)
        if re.match("Channel [0-9]*: Frequency [0-9]* .*", line):
            chan_num = int(re.findall(r"\d", line)[0])
            if chan_num not in range(num_chans):
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
def test_hello_world(xsig, fs, duration_ms, xsig_config, board_and_config, num_chans):
    # xflash the firmware
    board, config = board_and_config
    firmware = get_firmware_path(board, config)
    target_file = get_target_file(board)
    sh.xflash("--erase-all", "--target-file", target_file)
    sh.xflash("--no-compression", firmware)
    # Wait for device to enumerate
    time.sleep(10)
    # Run xsig
    xsig_output = sh.Command(xsig)(fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config)
    xsig_lines = xsig_output.split("\n")
    # Check output
    assert check_xsig_output(xsig_lines, num_chans)
