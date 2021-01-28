# Copyright (c) 2020, XMOS Ltd, All rights reserved
from contextlib import contextmanager
import os
from pathlib import Path
import platform
import pytest
import sh
import stat
import time
import re
import requests
import tempfile
from typing import List
import zipfile


XMOS_ROOT = Path(os.environ["XMOS_ROOT"])

AUDIO_BASE_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/audio"

# Taken from https://johnvansickle.com/ffmpeg/ and re-zipped
FFMPEG_LINUX_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/ffmpeg/linux/ffmpeg-4.3.1-amd64-static.zip"
XSIG_LINUX_URL = (
    "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/linux/xsig"
)
XMOSDFU_LINUX_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/linux/xmosdfu"

# Taken from https://evermeet.cx/ffmpeg/ and re-zipped
FFMPEG_MACOS_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/ffmpeg/macos/ffmpeg-100411-g32586a42da.zip"
XSIG_MACOS_URL = (
    "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/macos/xsig.zip"
)
XMOSDFU_MACOS_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/macos/xmosdfu.zip"

FFMPEG_PATH = Path(__file__).parent / "tools" / "ffmpeg" / "ffmpeg"
XSIG_PATH = Path(__file__).parent / "tools" / "xsig"
XMOSDFU_PATH = Path(__file__).parent / "tools" / "xmosdfu"
AUDIO_PATH = Path(__file__).parent / "audio"
XSIG_CONFIG_ROOT = XMOS_ROOT / "usb_audio_testing/xsig_configs"


# import hardware_test_tools # Required for SPDIF test
# TODO: Use hardware_test_tools!
# COPIED FROM HARDWARE_TEST_TOOLS:


def find_alsa_device(alsa_output, vendor_str_search="XMOS xCORE-200 MC"):
    """ Looks for the vendor_str_search in aplay or arecord output """

    vendor_str_found = False
    for line in alsa_output:
        if vendor_str_search not in line:
            continue
        vendor_str_found = True
        card_num = int(line[len("card ") : line.index(":")])
        dev_str = line[line.index("device") :]
        dev_num = int(dev_str[len("device ") : dev_str.index(":")])
    if not vendor_str_found:
        raise Exception(
            f'Could not find "{vendor_str_search}"" in alsa output:\n' f"{alsa_output}"
        )
    return card_num, dev_num


def find_aplay_device(vendor_str_search="XMOS xCORE-200 MC"):
    aplay_out = sh.aplay("-l")
    return find_alsa_device(aplay_out, vendor_str_search)


# /END COPIED FROM HARDWARE_TEST_TOOLS:


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
        lsusb_out = sh.lsusb("-v", "-d", f"{hex(vid)}:{hex(pid)}")

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
def audio(request, pytestconfig):
    """ Gets xsig from projects network drive """

    test_only = pytestconfig.getoption("test_only")

    if test_only:
        return [AUDIO_PATH / f for f in request.param]

    AUDIO_PATH.mkdir(parents=True, exist_ok=True)

    audio_paths = []
    for filename in request.param:
        print(filename)
        r = requests.get(f"{AUDIO_BASE_URL}/{filename}")
        with open(AUDIO_PATH / filename, "wb") as f:
            f.write(r.content)
        audio_paths.append(AUDIO_PATH / filename)
    return audio_paths


def get_xsig_config(build):
    """ Gets xsig configs for input and output signals """

    config_in = None
    config_out = None

    if build.chans_in == 10:
        if build.app == "xk_216_mc":
            config_in = "mc_analogue_input_8ch.json"
            config_out = "mc_analogue_output.json"
    elif build.chans_in == 2:
        if build.app == "xk_216_mc":
            config_in = "stereo_analogue_input.json"
            config_out = "stereo_analogue_output.json"
    if config_in is None:
        pytest.skip(f"No matching xsig configs for build: {build}")
    return config_in, config_out


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
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
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
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
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

    board = request.param.app
    config = request.param.config
    output_name = config

    if test_only:
        # Don't build anything
        # First 3 args specify the dfu/firmware names
        firmware = get_firmware_path(board, config, output_name)
    else:
        firmware, _ = build_board_config(board, config, output_name)

    if build_only:
        pytest.skip("--build-only is set")

    return firmware, request.param


@pytest.fixture
def build_with_dfu_test(request, pytestconfig):
    """ Builds firmware and creates a DFU test binary """

    build_only = pytestconfig.getoption("build_only")
    test_only = pytestconfig.getoption("test_only")

    assert not (build_only and test_only), "Build only and test only cannot both be set"

    board = request.param.app
    config = request.param.config
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
        pytest.skip("--build-only is set")

    return firmware, dfu_bin, request.param


def check_analyzer_output(
    analyzer_output: List[str], expected_frequencies: int, glitch_tolerance: int = 0
):
    """ Verify that the output from xsig is correct """

    glitches = [0 for _ in range(len(expected_frequencies))]

    failures = []
    # Check for any errors
    for line in analyzer_output:
        if re.match(".*ERROR|.*error|.*Error|.*Problem", line):
            if "glitch detected" in line:
                parse_line = line[len("ERROR: Channel ") :]
                chan = int(parse_line[: parse_line.index(":")])
                glitches[chan] += 1
            else:
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
                    wrong_frequency = int(line[len(channel_line) :].split()[0])
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
    # Check glitches
    for ch, g in enumerate(glitches):
        if g > glitch_tolerance:
            failures.append(
                f"Glitches on channel {ch} exceed glitch tolerance: "
                f"{g} > {glitch_tolerance}"
            )

    if len(failures) > 0:
        print("Checking analyser output failed:\n")
        print("\n".join(failures))
        return False
    return True


def run_audio_command(runtime, exe, *args):
    """ Run any command that needs to capture audio

    NOTE: If running on macOS on Jenkins, the environment WILL NOT be inherited
    by the child process
    """

    # If we're running on macOS on Jenkins, we need microphone permissions
    # To do this, we put an executable script in the $HOME/exec_all directory
    # A script is running on the host machine to execute everything in that dir
    if platform.system() == "Darwin":
        if "JENKINS" in os.environ:
            # Create a shell script to run the exe
            with tempfile.NamedTemporaryFile("w+", delete=True) as tmpfile:
                with tempfile.NamedTemporaryFile(
                    "w+", delete=False, dir=Path.home() / "exec_all"
                ) as script_file:
                    str_args = [str(a) for a in args]
                    # fmt: off
                    script_text = (
                        "#!/bin/bash\n"
                        f"{exe} {' '.join(str_args)} > {tmpfile.name}\n"
                    )
                    # fmt: on
                    script_file.write(script_text)
                    script_file.flush()
                    Path(script_file.name).chmod(
                        stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
                    )
                    time.sleep(runtime + 2)
                    stdout = tmpfile.read()
                    return stdout

    stdout = sh.Command(exe)(*args, _timeout=runtime)
    return stdout


@pytest.fixture(scope="session")
def ffmpeg(pytestconfig):
    """Gets ffmpeg from projects network drive """

    test_only = pytestconfig.getoption("test_only")

    if test_only:
        return FFMPEG_PATH

    FFMPEG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if platform.system() == "Darwin":
        r = requests.get(FFMPEG_MACOS_URL)
        zip_path = FFMPEG_PATH.parent / "ffmpeg.zip"
        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Unzip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(FFMPEG_PATH.parent)

        FFMPEG_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    elif platform.system() == "Linux":
        r = requests.get(FFMPEG_LINUX_URL)
        zip_path = FFMPEG_PATH.parent / "ffmpeg.zip"
        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Unzip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(FFMPEG_PATH.parent)

        FFMPEG_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    return FFMPEG_PATH


def find_audiotoolbox_device(device_name="XMOS xCORE-200 MC"):
    """ Find the audiotoolbox device index for use with ffmpeg """
    # fmt: off
    cmd_args = [
        "-f", "lavfi", "-i", "sine=r=44100:duration=0.01", # Input
        "-f", "audiotoolbox", "-list_devices", "true", "-" # Output
    ]
    # fmt: on
    new_env = os.environ.copy()
    new_env["AV_LOG_FORCE_NOCOLOR"] = "1"
    output = sh.Command(FFMPEG_PATH)(cmd_args, _err_to_out=True, _env=new_env)
    for line in output:
        if "[AudioToolbox @" in line:
            if device_name in line:
                num_text = line[line.index("]") + 1:]
                return int(num_text[num_text.index("[") + 1 : num_text.index("]")])
    raise Exception("Could not find audiotoolbox device")


def ffmpeg_output_device_args(device_name="XMOS xCORE-200 MC"):
    """ Returns a list of arguments to be appended to an ffmpeg command """

    if platform.system() == "Linux":
        card_num, dev_num = find_aplay_device(device_name)
        return ["-f", "alsa", f"hw:{card_num},{dev_num}"]
    elif platform.system() == "Darwin":
        dev_index = find_audiotoolbox_device(device_name)
        return ["-f", "audiotoolbox", str(dev_index)]


def ffmpeg_gen_sine_input_args(freqs, duration):
    """ Returns ffmpeg args for generating multi-channel sines """
    cmd_args = []
    for f in freqs:
        cmd_args += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={duration}"]
    cmd_args += ["-filter_complex", f"amerge=inputs={len(freqs)}"]
    return cmd_args
