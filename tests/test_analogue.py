# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    use_windows_builtin_driver,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features


samp_freqs = [44100, 48000, 88200, 96000, 176400, 192000]

# Run a reduced set of configs on Windows at the smoke level to keep the total duration reasonable
windows_smoke_configs = [
    "1AMi2o2xxxxxx",
    "2AMi10o10xssxxx",
    "2SSi8o8xxxxxx_tdm8",
    "2AMi8o8xxxxxx_winbuiltin",
]


def analogue_common_uncollect(fs, features, board, config, pytestconfig):
    # Sample rate not supported
    if features["max_freq"] < fs:
        return True
    level = pytestconfig.getoption("level")
    if (
        level == "smoke"
        and platform.system() == "Windows"
        and config not in windows_smoke_configs
    ):
        return True
    # XTAGs not present
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    if not all(xtag_ids):
        return True
    return False


def analogue_input_uncollect(pytestconfig, board, config, fs):
    features = get_config_features(board, config)
    if analogue_common_uncollect(fs, features, board, config, pytestconfig):
        return True
    if not features["analogue_i"]:
        # No input channels
        return True
    return False


def analogue_output_uncollect(pytestconfig, board, config, fs):
    features = get_config_features(board, config)
    if analogue_common_uncollect(fs, features, board, config, pytestconfig):
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
@pytest.mark.parametrize("fs", samp_freqs)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_input(pytestconfig, board, config, fs):
    features = get_config_features(board, config)

    xsig_config = f'mc_analogue_input_{features["analogue_i"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = (
            "mc_analogue_input_4ch"  # Requires jumper change to test > 4 channels
        )
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness) as harness,
        XsigInput(fs, duration, xsig_config_path, dut.dev_name) as xsig_proc,
    ):

        # Sleep for a few extra seconds so that xsig will have completed
        time.sleep(duration + 5)
        xsig_lines = xsig_proc.get_output()

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json["in"])


@pytest.mark.uncollect_if(func=analogue_output_uncollect)
@pytest.mark.parametrize("fs", samp_freqs)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_output(pytestconfig, board, config, fs):
    features = get_config_features(board, config)

    # Issue 120
    if (
        platform.system() == "Windows"
        and board == "xk_316_mc"
        and config == "2AMi8o8xxxxxx_winbuiltin"
        and fs in [44100, 48000]
    ):
        pytest.xfail("Glitches can occur")

    xsig_config = f'mc_analogue_output_{features["analogue_o"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = "mc_analogue_output_2ch"
    elif board == "xk_216_mc" and features["tdm8"] and features["i2s"] == "S":
        xsig_config += "_paired"  # Pairs of channels can be swapped in hardware
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
        XsigOutput(fs, None, xsig_config_path, dut.dev_name),
    ):

        time.sleep(duration)
        harness.terminate()
        xscope_lines = harness.get_output()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xscope_lines, xsig_json["out"])
