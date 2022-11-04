# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
import io
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
)
from conftest import list_configs, get_config_features


samp_freqs = [44100, 48000, 88200, 96000, 176400, 192000]


def analogue_common_uncollect(fs, features):
    # Sample rate not supported
    return features["max_freq"] < fs


def analogue_input_uncollect(level, board_config, fs):
    features = get_config_features(board_config)
    if analogue_common_uncollect(fs, features):
        return True
    if not features["analogue_i"]:
        # No input channels
        return True
    return False


def analogue_output_uncollect(level, board_config, fs):
    features = get_config_features(board_config)
    if analogue_common_uncollect(fs, features):
        return True
    if not features["analogue_o"]:
        # No output channels
        return True
    return False


def analogue_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration


@pytest.mark.uncollect_if(func=analogue_input_uncollect)
@pytest.mark.parametrize("board_config", list_configs())
@pytest.mark.parametrize("fs", samp_freqs)
def test_analogue_input(pytestconfig, xtag_wrapper, xsig, board_config, fs):
    features = get_config_features(board_config)
    xsig_config = f'mc_analogue_input_{features["analogue_i"]}ch'
    if "xk_316_mc" in board_config and features["tdm8"]:
        xsig_config = (
            "mc_analogue_input_4ch"  # Requires jumper change to test > 4 channels
        )
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
    adapter_dut, adapter_harness = xtag_wrapper

    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])

    board_config = board_config.split("-", maxsplit=1)
    board = board_config[0]
    config = board_config[1]

    # xrun the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    subprocess.run(
        ["xrun", "--adapter-id", adapter_harness, harness_firmware], check=True
    )
    # xflash the firmware
    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    # Run xsig
    xsig_duration = duration + 5
    with tempfile.NamedTemporaryFile(mode="w+") as out_file:
        run_audio_command(
            out_file, xsig, f"{fs}", f"{duration * 1000}", xsig_config_path
        )
        time.sleep(xsig_duration)
        out_file.seek(0)
        xsig_lines = out_file.readlines()

    # Harness is still running, so break in with xgdb to stop it
    subprocess.check_output(
        [
            "xgdb",
            f"--eval-command=connect --adapter-id {adapter_harness}",
            "--eval-command=quit",
        ]
    )

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json["in"])


@pytest.mark.uncollect_if(func=analogue_output_uncollect)
@pytest.mark.parametrize("board_config", list_configs())
@pytest.mark.parametrize("fs", samp_freqs)
def test_analogue_output(pytestconfig, xtag_wrapper, xsig, board_config, fs):
    features = get_config_features(board_config)
    xsig_config = f'mc_analogue_output_{features["analogue_o"]}ch'
    if "xk_316_mc" in board_config and features["tdm8"]:
        xsig_config = "mc_analogue_output_2ch"
    elif "xk_216_mc" in board_config and features["tdm8"] and features["i2s"] == "S":
        xsig_config += "_paired"  # Pairs of channels can be swapped in hardware
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
    adapter_dut, adapter_harness = xtag_wrapper

    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])

    board_config = board_config.split("-", maxsplit=1)
    board = board_config[0]
    config = board_config[1]

    # xrun the dut
    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    # xrun --xscope the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    harness_proc = subprocess.Popen(
        ["xrun", "--adapter-id", adapter_harness, "--xscope", harness_firmware],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Run xsig for duration + 2 seconds
    xsig_proc = subprocess.Popen(
        [xsig, f"{fs}", f"{(duration + 2) * 1000}", xsig_config_path]
    )
    time.sleep(duration)

    harness_proc.send_signal(signal.SIGINT)
    xsig_proc.terminate()

    xscope_str = harness_proc.stdout.read()
    xscope_lines = xscope_str.splitlines()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xscope_lines, xsig_json["out"])
