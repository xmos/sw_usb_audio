# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features

loopback_configs = [
    ("xk_316_mc", "2AMi8o8xxxxxx_i2sloop"),
]

def i2s_loop_uncollect(pytestconfig, board, config):
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        return True
    return False

def i2s_loop_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 10
    return duration

@pytest.mark.uncollect_if(func=i2s_loop_uncollect)
@pytest.mark.parametrize(["board", "config"], loopback_configs)
def test_i2s_loopback(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_i2s_loopback_8ch.json"

    adapter_dut = get_xtag_dut(pytestconfig, board)
    duration = i2s_loop_duration(pytestconfig.getoption("level"), features["partial"])
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