# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
import tempfile
import signal

from usb_audio_test_utils import (
    wait_for_portaudio,
    get_firmware_path_harness,
    get_firmware_path,
    run_audio_command,
    check_analyzer_output,
    get_xscope_port_number,
    wait_for_xscope_port,
)
from conftest import list_configs, get_config_features


samp_freqs = [44100, 48000, 88200, 96000, 176400, 192000]


def spdif_common_uncollect(fs, features):
    return features["max_freq"] < fs


def spdif_input_uncollect(level, board_config, fs):
    features = get_config_features(board_config)
    return any([not features["spdif_i"], spdif_common_uncollect(fs, features)])


def spdif_output_uncollect(level, board_config, fs):
    features = get_config_features(board_config)
    return any([not features["spdif_o"], spdif_common_uncollect(fs, features)])


def spdif_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration


@pytest.mark.uncollect_if(func=spdif_input_uncollect)
@pytest.mark.parametrize("fs", samp_freqs)
@pytest.mark.parametrize("board_config", list_configs())
def test_spdif_input(pytestconfig, xtag_wrapper, xsig, board_config, fs):
    features = get_config_features(board_config)
    xsig_config = f'mc_digital_input_{features["analogue_i"]}ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
    adapter_dut, adapter_harness = xtag_wrapper

    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])

    board_config = board_config.split("-", maxsplit=1)
    board = board_config[0]
    config = board_config[1]

    xscope_port = get_xscope_port_number()

    # Run the harness and set the sample rate for the ramp signal
    harness_firmware = get_firmware_path_harness("xcore200_mc", config="spdif_test")
    harness_proc = subprocess.Popen(
        [
            "xrun",
            "--adapter-id",
            adapter_harness,
            "--xscope-port",
            f"localhost:{xscope_port}",
            harness_firmware,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    wait_for_xscope_port(xscope_port)

    xscope_controller = (
        Path(__file__).parents[2]
        / "sw_audio_analyzer"
        / "host_xscope_controller"
        / "bin_macos"
        / "xscope_controller"
    )
    subprocess.run([xscope_controller, "localhost", f"{xscope_port}", "0", f"f {fs}"])

    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware])

    wait_for_portaudio(board, config)

    volcontrol_path = Path(__file__).parent / "tools" / "volcontrol" / "volcontrol"
    subprocess.run([volcontrol_path, "--clock", "SPDIF"])

    # Run xsig
    xsig_duration = duration + 5
    with tempfile.NamedTemporaryFile(mode="w+") as out_file:
        run_audio_command(
            out_file, xsig, f"{fs}", f"{duration * 1000}", xsig_config_path
        )
        time.sleep(xsig_duration)
        out_file.seek(0)
        xsig_lines = out_file.readlines()

    harness_proc.send_signal(signal.SIGINT)

    # Return to using to the internal clock
    subprocess.run([volcontrol_path, "--clock", "Internal"])

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json["in"])


@pytest.mark.uncollect_if(func=spdif_output_uncollect)
@pytest.mark.parametrize("fs", samp_freqs)
@pytest.mark.parametrize("board_config", list_configs())
def test_spdif_output(pytestconfig, xtag_wrapper, xsig, board_config, fs):
    features = get_config_features(board_config)
    xsig_config = f'mc_digital_output_{features["analogue_o"]}ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
    adapter_dut, adapter_harness = xtag_wrapper

    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])

    board_config = board_config.split("-", maxsplit=1)
    board = board_config[0]
    config = board_config[1]

    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware])

    wait_for_portaudio(board, config)

    # Run xsig for longer than the test duration as it will be terminated later
    xsig_duration_ms = (duration + 100) * 1000
    xsig_proc = subprocess.Popen(
        [xsig, f"{fs}", f"{xsig_duration_ms}", xsig_config_path]
    )

    harness_firmware = get_firmware_path_harness("xcore200_mc", config="spdif_test")
    harness_proc = subprocess.Popen(
        ["xrun", "--adapter-id", adapter_harness, "--xscope", harness_firmware],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    time.sleep(duration)

    harness_proc.send_signal(signal.SIGINT)
    xscope_str = harness_proc.stdout.read()
    xscope_lines = xscope_str.splitlines()

    xsig_proc.terminate()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    check_analyzer_output(xscope_lines, xsig_json["out"])
