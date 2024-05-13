# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut,
    XrunDut,
    XsigInput,
)
from conftest import list_configs, get_config_features


def OS_uncollect(features, board, config):
    if (
        platform.system() == "Darwin"
        and board == "xk_316_mc"
        and "2AMi2o2xxxxxx" in config
    ):
        # macOS defaults to the 16-bit audio profile on this config and xsig and portaudio are not forcing a change in bit depth
        return True
    return False

def loopback_dac_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        # XTAGs not present
        return True
    if OS_uncollect(features, board, config):
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

@pytest.mark.uncollect_if(func=loopback_dac_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_loopback_dac(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_i2s_loopback_{features["analogue_o"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = "mc_i2s_loopback_2ch"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut = get_xtag_dut(pytestconfig, board)
    duration = analogue_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    samp_freqs = [f for f in features["samp_freqs"] if f <= 96000] # TODO Extend to 192KHz, 10ch as part of ADAT output for SMUX > 1 testing
    with XrunDut(adapter_dut, board, config) as dut:
        for fs in samp_freqs:
            # Issue 120
            if (
                platform.system() == "Windows"
                and board == "xk_316_mc"
                and "winbuiltin" in config
                and fs in [44100, 48000]
            ):
                continue

            dut.set_stream_format("input", fs, features["chan_i"], 24)
            dut.set_stream_format("output", fs, features["chan_o"], 24)

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
