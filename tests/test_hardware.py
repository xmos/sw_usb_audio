# Copyright (c) 2020, XMOS Ltd, All rights reserved
from contextlib import contextmanager
import io
import os
from pathlib import Path
import platform
import pytest
import sh
import stat
import time
import re
import requests
from typing import List
import xtagctl
import zipfile

# import hardware_test_tools # Required for SPDIF test

XMOS_ROOT = Path(os.environ["XMOS_ROOT"])

XSIG_LINUX_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/linux/xsig"
XMOSDFU_LINUX_URL = (
    "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/linux/xmosdfu"
)
XSIG_MACOS_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/macos/xsig.zip"
XMOSDFU_MACOS_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/macos/xmosdfu.zip"

XSIG_PATH = Path(__file__).parent / "tools" / "xsig"
XMOSDFU_PATH = Path(__file__).parent / "tools" / "xmosdfu"
XSIG_CONFIG_ROOT = XMOS_ROOT / "usb_audio_testing/xsig_configs"


@contextmanager
def pushd(new_dir):
    last_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(last_dir)


def set_clock_source_alsa(card_num, source: str):
    """ Sets the clock source of the USB audio device """

    if source == "INTERNAL":
        sh.amixer(
            f"-c{card_num}",
            "set",
            "XMOS Clock Selector Clock Source",
            "XMOS Internal Clock",
        )
    elif source == "SPDIF":
        sh.amixer(
            f"-c{card_num}",
            "set",
            "XMOS Clock Selector Clock Source",
            "XMOS S/PDIF Clock",
        )


def get_bcd_version(vid: int, pid: int) -> str:
    """Gets the BCD Device version number for a connected USB device with the
    specified VID and PID

    TODO: Windows support
    """

    if platform.system() == "Darwin":
        prof_out = sh.system_profiler.SPUSBDataType()
        prof_lines = prof_out.split("\n")
        xcore_lines = []
        current_pid = None
        current_vid = None
        for i, line in enumerate(prof_lines):
            if line.strip().startswith("Product ID:"):
                current_pid = int(line.split()[2], 16)
            if line.strip().startswith("Vendor ID:"):
                current_vid = int(line.split()[2], 16)
            if line.strip().startswith("Version"):
                if current_pid == pid and current_vid == vid:
                    return line.split()[1].strip()

        raise Exception(f"BCD Device not found: \n{prof_out}")
    elif platform.system() == "Linux":
        lsusb_out = sh.lsusb("-v", "-d", f"{vid}:{pid}")

        for line in lsusb_out.split("\n"):
            if line.strip().startswith("bcdDevice"):
                version_str = line.split()[1]
                return version_str.strip()

        raise Exception(f"BCD Device not found: \n{lsusb_out}")


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


def get_app_path(board):
    """ Gets the path to the app folder for a given board """

    app_path = XMOS_ROOT / "sw_usb_audio" / f"app_usb_aud_{board}"
    return app_path


def get_firmware_path(board, config, output_name=None):
    """ Gets the path to the firmware binary """

    firmware_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.xe"
    )
    if output_name is not None:
        firmware_path = firmware_path.parent.parent / (output_name + ".xe")
    return firmware_path


def get_dfu_bin_path(board, config, output_name=None):
    """ Gets the path to the DFU binary """

    dfu_bin_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.bin"
    )
    if output_name is not None:
        dfu_bin_path = dfu_bin_path.parent.parent / (output_name + ".bin")
    return dfu_bin_path


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
    """ Gets xsig from projects network drive """

    XSIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if platform.system() == "Darwin":
        r = requests.get(XSIG_MACOS_URL)
        zip_path = XSIG_PATH.parent / "xsig.zip"
        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Unzip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(XSIG_PATH.parent)

        XSIG_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    elif platform.system() == "Linux":
        r = requests.get(XSIG_LINUX_URL)
        with open(XSIG_PATH, "wb") as f:
            f.write(r.content)

        XSIG_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    return XSIG_PATH


@pytest.fixture
def xmosdfu():
    """Gets xmosdfu from projects network drive """

    XMOSDFU_PATH.parent.mkdir(parents=True, exist_ok=True)

    if platform.system() == "Darwin":
        r = requests.get(XMOSDFU_MACOS_URL)
        zip_path = XMOSDFU_PATH.parent / "xmosdfu.zip"
        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Unzip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(XMOSDFU_PATH.parent)

        XMOSDFU_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    elif platform.system() == "Linux":

        r = requests.get(XMOSDFU_LINUX_URL)
        with open(XMOSDFU_PATH, "wb") as f:
            f.write(r.content)

        XMOSDFU_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    return XMOSDFU_PATH


def create_dfu_bin(board, config):
    """ Calls xflash on an existing firmware binary to create a DFU binary """

    firmware_path = get_firmware_path(board, config)
    dfu_bin_path = get_dfu_bin_path(board, config)
    sh.xflash(
        "--factory-version",
        "14.3",
        "--upgrade",
        "1",
        firmware_path,
        "-o",
        dfu_bin_path,
        "--no-compression",
    )
    return dfu_bin_path


def build_board_config(board, config, output_name=None, xmake_args=[]):
    """This function builds firmware with any specified xmake args
    and returns paths to the resulting xe and bin files
    """
    app_path = get_app_path(board)
    with pushd(app_path):
        # Clean
        sh.xmake.clean(f"CONFIG={config}", "FULL=1", *xmake_args)
        # Make
        sh.xmake(f"CONFIG={config}", "FULL=1", *xmake_args)
        # Create a DFU bin
        dfu_bin_path = create_dfu_bin(board, config)

    firmware_path = get_firmware_path(board, config)

    if output_name is not None:
        # Rename if output_name is given
        output_firmware_path = get_firmware_path(board, config, output_name)
        output_dfu_bin_path = get_dfu_bin_path(board, config, output_name)
        firmware_path.rename(output_firmware_path)
        dfu_bin_path.rename(output_dfu_bin_path)
        return output_firmware_path, output_dfu_bin_path

    return firmware_path, dfu_bin_path


@pytest.fixture
def build(request, pytestconfig):
    """ Builds firmware only """

    build_only = pytestconfig.getoption("build_only")
    test_only = pytestconfig.getoption("test_only")

    assert not (build_only and test_only), "Build only and test only cannot both be set"

    board, config = request.param[:2]
    output_name = config

    if test_only:
        # Don't build anything
        # First 3 args specify the dfu/firmware names
        firmware = get_firmware_path(board, config, output_name)
    else:
        firmware, _ = build_board_config(board, config, output_name)

    if build_only:
        return None  # Signal to the test to skip

    return firmware


@pytest.fixture
def build_with_dfu_test(request, pytestconfig):
    """ Builds firmware and creates a DFU test binary """

    build_only = pytestconfig.getoption("build_only")
    test_only = pytestconfig.getoption("test_only")

    assert not (build_only and test_only), "Build only and test only cannot both be set"

    board, config = request.param[:2]
    factory_output_name = config
    dfu_output_name = config + "_dfu"

    if test_only:
        # Don't build anything
        # First 3 args specify the dfu/firmware names
        firmware = get_firmware_path(board, config, factory_output_name)
        dfu_bin = get_dfu_bin_path(board, config, dfu_output_name)
    else:
        firmware, _ = build_board_config(board, config, factory_output_name)
        _, dfu_bin = build_board_config(
            board, config, dfu_output_name, xmake_args=["TEST_DFU_1=1"]
        )

    if build_only:
        return None  # Signal to the test to skip

    return firmware, dfu_bin


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
        channel_line = f"Channel {i}: Frequency "
        expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
        wrong_frequency = None
        for line in analyzer_output:
            if line.startswith(channel_line):
                if line.startswith(expected_line):
                    found = True
                else:
                    # Remove the prefix, split by whitespace, take the first element
                    wrong_frequency = int(line[len(channel_line):].split()[0])
        if not found:
            if wrong_frequency is None:
                failures.append(f"No signal seen on channel {i}")
            else:
                failures.append(
                    f"Incorrect frequency seen on channel {i}. "
                    f"Expected {expected_freq}, got {wrong_frequency}."
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
        print("Checking analyser output failed:\n")
        print("\n".join(failures))
        return False
    return True


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_input_8ch.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i8o8xxxxx_tdm8")], indirect=True)
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_input(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_dut:
        with xtagctl.target("usb_audio_mc_xs2_harness") as adapter_harness:
            # Reset both xtags
            xtagctl.reset_adapter(adapter_dut)
            xtagctl.reset_adapter(adapter_harness)
            time.sleep(2)  # Wait for adapters to enumerate
            # xrun the harness
            harness_firmware = get_firmware_path_harness("xcore200_mc")
            sh.xrun("--adapter-id", adapter_harness, harness_firmware)
            # xflash the firmware
            firmware = build
            sh.xrun("--adapter-id", adapter_dut, firmware)
            # Wait for device to enumerate
            time.sleep(10)
            # Run xsig
            xsig_output = sh.Command(xsig)(
                fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config
            )
            xsig_lines = xsig_output.split("\n")
            # Check output
            expected_freqs = [(i + 1) * 1000 for i in range(num_chans)]
            assert check_analyzer_output(xsig_lines, expected_freqs)


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_output.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i8o8xxxxx_tdm8")], indirect=True)
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_output(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_dut:
        with xtagctl.target("usb_audio_mc_xs2_harness") as adapter_harness:
            print(f"Adapter DUT: {adapter_dut}, Adapter harness: {adapter_harness}")
            # Reset both xtags
            xtagctl.reset_adapter(adapter_dut)
            xtagctl.reset_adapter(adapter_harness)
            time.sleep(2)  # Wait for adapters to enumerate
            # xrun the dut
            firmware = build
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
                _bg_exc=False,
            )
            # Wait for device(s) to enumerate
            time.sleep(10)
            # Run xsig for duration_ms + 2 seconds
            xsig_cmd = sh.Command(xsig)(
                fs, duration_ms + 2000, XSIG_CONFIG_ROOT / xsig_config, _bg=True
            )
            time.sleep(duration_ms / 1000)
            # Get analyser output
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
            # Wait for xsig to exit (timeout after 5 seconds)
            xsig_cmd.wait(timeout=5)

            expected_freqs = [((i + 1) * 1000) + 500 for i in range(num_chans)]
            assert check_analyzer_output(xscope_lines, expected_freqs)


@pytest.mark.skip(reason="SPDIF test is WIP")
@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_digital_input_8ch.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i16o16xxxaax")], indirect=True)
@pytest.mark.parametrize("num_chans", [10])
def test_spdif_input(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_dut:
        with xtagctl.target("usb_audio_mc_xs2_harness") as adapter_harness:
            # Reset both xtags
            xtagctl.reset_adapter(adapter_dut)
            xtagctl.reset_adapter(adapter_harness)
            time.sleep(2)  # Wait for adapters to enumerate
            # xrun the harness
            harness_firmware = get_firmware_path_harness("xcore200_mc")
            sh.xrun("--adapter-id", adapter_harness, harness_firmware)
            # xflash the firmware
            firmware = build
            sh.xrun("--adapter-id", adapter_dut, firmware)
            # Wait for device to enumerate
            time.sleep(10)
            # Set the clock source to SPDIF
            card_num, dev_num = hardware_test_tools.find_aplay_device("xCORE USB Audio")
            set_clock_source_alsa(card_num, "SPDIF")
            # Run xsig
            xsig_output = sh.Command(xsig)(
                fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config
            )
            xsig_lines = xsig_output.split("\n")
            # Check output
            # expected_freqs = [(i+1) * 1000 for i in range(num_chans)]
            # assert check_analyzer_output(xsig_lines, expected_freqs)


@pytest.mark.parametrize(
    "build_with_dfu_test", [("xk_216_mc", "2i10o10xxxxxx")], indirect=True
)
def test_dfu(xmosdfu, build_with_dfu_test):
    if build_with_dfu_test is None:
        pytest.skip("Build not present")
    with xtagctl.target("usb_audio_mc_xs2_dut") as adapter_dut:
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        time.sleep(2)  # Wait for adapters to enumerate
        # xflash the firmware
        firmware, dfu_bin = build_with_dfu_test
        sh.xflash("--adapter-id", adapter_dut, "--no-compression", firmware)
        # Wait for device to enumerate
        time.sleep(10)
        # Run DFU test procedure
        initial_version = get_bcd_version(0x20b1, 0x8)
        # Download the new firmware
        try:
            sh.Command(xmosdfu)("0x8", "--download", dfu_bin)
        except sh.ErrorReturnCode as e:
            print(e.stdout)
            raise Exception()
        time.sleep(3)
        # Check version
        upgrade_version = get_bcd_version(0x20b1, 0x8)
        # Revert to factory
        sh.Command(xmosdfu)("0x8", "--revertfactory")
        time.sleep(3)
        # Check version
        reverted_version = get_bcd_version(0x20b1, 0x8)

        assert initial_version == reverted_version
        assert upgrade_version != initial_version


# if __name__ == "__main__":
#    test_analogue_output(
#        Path("./xsig").resolve(),
#        48000,
#        10000,
#        "mc_analogue_output.json",
#        ("xk_216_mc", "2i8o8xxxxx_tdm8"),
#        8,
#    )
