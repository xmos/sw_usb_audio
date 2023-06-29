# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    get_xtag_dut,
    use_windows_builtin_driver,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features


# Run a reduced set of configs on Windows at the smoke level to keep the total duration reasonable
windows_smoke_configs = [
    "1AMi2o2xxxxxx",
    "2AMi2o2xxxxxx",
    "2AMi10o10xssxxx",
    "2SSi8o8xxxxxx_tdm8",
    "2AMi8o8xxxxxx_winbuiltin",
    "2AMi2o2xxxxxx_winbuiltin",
]

def analogue_OS_unclollect(features, board, config, pytestconfig):
    level = pytestconfig.getoption("level")
    if (
        level == "smoke"
        and platform.system() == "Windows"
        and config not in windows_smoke_configs
        and config.removesuffix("_i2sloopback") not in windows_smoke_configs
    ):
        return True
    if (
        platform.system() == "Darwin"
        and board == "xk_316_mc"
        and "2AMi2o2xxxxxx" in config
    ):
        # macOS defaults to the 16-bit audio profile on this config and xsig and portaudio are not forcing a change in bit depth
        return True
    return False

def analogue_require_dut_and_harness(features, board, config, pytestconfig):
    # XTAGs not present
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    if not all(xtag_ids):
        return True
    return False
    
def analogue_non_loopback_common_uncollect(features, board, config, pytestconfig):
    level = pytestconfig.getoption("level")
    if (
        level == "smoke"
        and board == "xk_316_mc"
    ):
        return True
    if analogue_OS_unclollect(features, board, config, pytestconfig):
        return True
    if analogue_require_dut_and_harness(features, board, config, pytestconfig):
        return True
    if features["i2s_loopback"]:
        return True
    return False

def analogue_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    if analogue_non_loopback_common_uncollect(features, board, config, pytestconfig):
        return True
    if not features["analogue_i"]:
        # No input channels
        return True
    return False

def analogue_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    if analogue_non_loopback_common_uncollect(features, board, config, pytestconfig):
        return True
    if not features["analogue_o"]:
        # No output channels
        return True
    return False

def analogue_loopback_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        # XTAGs not present
        return True
    if analogue_OS_unclollect(features, board, config, pytestconfig):
        return True
    if not features["i2s_loopback"]:
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
        duration = 10
    return duration


@pytest.mark.uncollect_if(func=analogue_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_analogue_input_{features["analogue_i"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = (
            "mc_analogue_input_4ch"  # Requires jumper change to test > 4 channels
        )
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    short_test = features["partial"] or board == "xk_316_mc"
    duration = analogue_duration(pytestconfig.getoption("level"), short_test)
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness) as harness,
    ):
        for fs in features["samp_freqs"]:
            with XsigInput(fs, duration, xsig_config_path, dut.dev_name) as xsig_proc:
                # Sleep for a few extra seconds so that xsig will have completed
                time.sleep(duration + 6)
                xsig_lines = xsig_proc.get_output()

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += "\n".join(xsig_lines) + "\n\n"

    if len(fail_str) > 0:
        harness_output = harness.get_output()
        if len(harness_output) > 0:
            fail_str += "Audio analyzer stdout\n"
            fail_str += "\n".join(harness_output)
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=analogue_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_output(pytestconfig, board, config):
    features_tmp = get_config_features(board, config)
    features = features_tmp.copy()

    xsig_config = f'mc_analogue_output_{features["analogue_o"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = "mc_analogue_output_2ch"
    elif board == "xk_216_mc" and features["tdm8"] and features["i2s"] == "S":
        xsig_config += "_paired"  # Pairs of channels can be swapped in hardware
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    short_test = features["partial"] or board == "xk_316_mc"
    duration = analogue_duration(pytestconfig.getoption("level"), short_test)
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            # Issue 120
            if (
                platform.system() == "Windows"
                and board == "xk_316_mc"
                and config == "2AMi8o8xxxxxx_winbuiltin"
                and fs in [44100, 48000]
            ):
                continue

            with (
                AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
                XsigOutput(fs, None, xsig_config_path, dut.dev_name),
            ):

                time.sleep(duration)
                harness.terminate()
                xscope_lines = harness.get_output()

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xscope_lines, xsig_json["out"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xscope stdout at sample rate {fs}\n"
                fail_str += "\n".join(xscope_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=analogue_loopback_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_loopback(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_i2s_loopback_{features["analogue_o"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = "mc_i2s_loopback_2ch"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut = get_xtag_dut(pytestconfig, board)
    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            with XsigInput(fs, duration, xsig_config_path, dut.dev_name) as xsig_proc:
                time.sleep(duration + 6)
                xsig_lines = xsig_proc.get_output()
            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
        if len(failures) > 0:
            fail_str += f"Failure at sample rate {fs}\n"
            fail_str += "\n".join(failures) + "\n\n"
            fail_str += f"xsig stdout at sample rate {fs}\n"
            fail_str += "\n".join(xsig_lines) + "\n\n"


    if len(fail_str) > 0:
        pytest.fail(fail_str)
