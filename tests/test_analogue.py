# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
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
import tempfile
from typing import List
import xtagctl
import zipfile


XMOS_ROOT = Path(os.environ["XMOS_ROOT"])
XSIG_LINUX_URL = (
    "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/linux/xsig"
)
XSIG_MACOS_URL = (
    "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/macos/xsig.zip"
)
XSIG_PATH = Path(__file__).parent / "tools" / "xsig"
XSIG_CONFIG_ROOT = XMOS_ROOT / "usb_audio_testing/xsig_configs"


def wait_for_enumeration(pid, vid, timeout=10):
    for _ in range(timeout):
        time.sleep(1)

        if platform.system() == "Darwin":
            prof_out = sh.system_profiler.SPUSBDataType()
            prof_lines = prof_out.split("\n")
            current_pid = None
            current_vid = None
            for line in prof_lines:
                if line.strip().startswith("Product ID:"):
                    current_pid = int(line.split()[2], 16)
                if line.strip().startswith("Vendor ID:"):
                    current_vid = int(line.split()[2], 16)
                if current_pid == pid and current_vid == vid:
                    return
        elif platform.system() == "Linux":
            lsusb_out = sh.lsusb("-v", "-d", f"{hex(vid)}:{hex(pid)}")
            for line in lsusb_out.split("\n"):
                if line.strip().startswith("bcdDevice"):
                    return

    assert False, f"Device failed to enumerate in {timeout}s"


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
    """ Gets the path to the firmware binary """

    firmware_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.xe"
    )
    return firmware_path


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
                with tempfile.NamedTemporaryFile("w+", delete=False, dir=Path.home() / "exec_all") as script_file:
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


def mark_tests(level_mark, testcases):
    return [pytest.param(*tc, marks=level_mark) for tc in testcases]


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, number of channels)
analogue_input_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        96000, 10, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  48000, 10, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  96000, 10, 8),
        ('xk_216_mc', '2i10o10xxxxxx',         192000, 10, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 10, 8),
        ('xk_216_mc', '2i10o10msxxxx',         192000, 10, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',    192000, 10, 8),
        ('xk_216_mc', '2i10o10xssxxx',         192000, 10, 8)
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        #('xk_216_mc', '2i8o8xxxxxx_tdm8',        44100, 600, 8),
        #('xk_216_mc', '2i8o8xxxxxx_tdm8_slave',  44100, 600, 8),
        ('xk_216_mc', '2i10o10xxxxxx',           48000, 600, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    192000, 600, 8),
        ('xk_216_mc', '2i10o10msxxxx',           48000, 600, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 600, 8),
        ('xk_216_mc', '2i10o10xssxxx',           48000, 600, 8),
        ('xk_216_mc', '2i10o10xsxxxd',           48000, 600, 8),
        ('xk_216_mc', '2i10o10xsxxxd',          192000, 600, 8),
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        #('xk_216_mc', '2i8o8xxxxx_tdm8',         48000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',         88200, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',         96000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   48000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   88200, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',           44100, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',           88200, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',           96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',          176400, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     44100, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     48000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     88200, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    176400, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    192000, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',           44100, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',           88200, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',           96000, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',          176400, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      44100, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      96000, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     176400, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',           44100, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',           88200, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',           96000, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',          176400, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxd',           44100, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxd',           88200, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxd',           96000, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxd',          176400, 1800, 8)
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "num_chans"], analogue_input_configs)
def test_analogue_input(xsig, board, config, fs, duration, num_chans):
    if num_chans == 8:
        xsig_config = "mc_analogue_input_8ch.json"
    else:
        assert False, f"Invalid channel count {num_chans}"

    duration_ms = duration * 1000

    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        # xrun the harness
        harness_firmware = get_firmware_path_harness("xcore200_mc")
        sh.xrun("--adapter-id", adapter_harness, harness_firmware)
        # xflash the firmware
        firmware = get_firmware_path(board, config)
        sh.xrun("--adapter-id", adapter_dut, firmware)

        wait_for_enumeration(0x8, 0x20B1)

        # Run xsig
        xsig_duration = (duration_ms / 1000) + 5
        xsig_output = run_audio_command(
            xsig_duration, xsig, fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config
        )
        xsig_lines = xsig_output.split("\n")
        # Check output
        expected_freqs = [(i + 1) * 1000 for i in range(num_chans)]
        assert check_analyzer_output(xsig_lines, expected_freqs)


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, number of channels)
analogue_output_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        #('xk_216_mc', '1i2o2xxxxxx',            48000, 10, 2),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        96000, 10, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  48000, 10, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  96000, 10, 8),
        ('xk_216_mc', '2i10o10xxxxxx',         192000, 10, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 10, 8),
        ('xk_216_mc', '2i10o10msxxxx',         192000, 10, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',    192000, 10, 8),
        ('xk_216_mc', '2i10o10xssxxx',         192000, 10, 8)
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        #('xk_216_mc', '1i2o2xxxxxx',            44100, 600, 2),
        #('xk_216_mc', '1i2o2xxxxxx',            48000, 600, 2),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        44100, 600, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  44100, 600, 8),
        ('xk_216_mc', '2i10o10xxxxxx',          48000, 600, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 600, 8),
        ('xk_216_mc', '2i10o10msxxxx',          48000, 600, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     48000, 600, 8),
        ('xk_216_mc', '2i10o10xssxxx',          48000, 600, 8)
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        #('xk_216_mc', '1i2o2xxxxxx',            44100, 1800, 2),
        #('xk_216_mc', '1i2o2xxxxxx',            48000, 1800, 2),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        48000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        88200, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8',        96000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  48000, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  88200, 1800, 8),
        #('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',          44100, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',          88200, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',          96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx',         176400, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    44100, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    48000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    88200, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    96000, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   176400, 1800, 8),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',          44100, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',          88200, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',          96000, 1800, 8),
        ('xk_216_mc', '2i10o10msxxxx',         176400, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     44100, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     88200, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     96000, 1800, 8),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',    176400, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',          44100, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',          88200, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',          96000, 1800, 8),
        ('xk_216_mc', '2i10o10xssxxx',         176400, 1800, 8)
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "num_chans"], analogue_output_configs)
def test_analogue_output(xsig, board, config, fs, duration, num_chans):
    if num_chans == 8:
        xsig_config = "mc_analogue_output.json"
    else:
        assert False, f"Invalid channel count {num_chans}"

    duration_ms = duration * 1000

    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        # xrun the dut
        firmware = get_firmware_path(board, config)
        sh.xrun("--adapter-id", adapter_dut, firmware)
        # sleep to workaround bug where running the harness firmware can fail
        time.sleep(1)
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

        wait_for_enumeration(0x8, 0x20B1)

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
