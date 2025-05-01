# Copyright 2020-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
from pathlib import Path
import pytest
import time
import json
import platform

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.Xsig import XsigInput
from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut

if platform.system() == "Darwin":
    loopback_smoke_configs = [
        ("xk_316_mc", "2AMi18o18mssaax_i2sloopback"),
        ("xk_316_mc", "2AMi8o8xxxxxx_mix8_i2sloopback"),
        ("xk_316_mc", "2SSi8o8xxxxxx_i2sloopback"),
        ("xk_316_mc", "2AMi30o30xxxxxx_hibw_i2sloopback"),
        ("xk_316_mc", "2AMi20o20xxxaax_hibw_i2sloopback"),
    ]
else:
    loopback_smoke_configs = [
        ("xk_316_mc", "2AMi18o18mssaax_i2sloopback"),
        ("xk_316_mc", "2AMi20o20xxxaax_hibw_i2sloopback"),
        ("xk_316_mc", "2AMi30o30xxxxxx_hibw_i2sloopback"),
    ]


def loopback_dac_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        # XTAGs not present
        return True
    if not features["i2s_loopback"]:
        return True
    if not features["analogue_o"]:
        # No output channels
        return True
    if pytestconfig.getoption("level") == "smoke" and (board, config) not in loopback_smoke_configs:
        return True
    return False

def loopback_dac_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
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
    duration = loopback_dac_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            # Issue 120
            if (
                platform.system() == "Windows"
                and board == "xk_316_mc"
                and "winbuiltin" in config
                and fs in [44100, 48000]
            ):
                continue
            if not features["hibw"]:
                if fs > 96000:
                    max_num_channels = 10
                    dut.set_stream_format("input", fs, min(max_num_channels, features["chan_i"]), 24)
                    dut.set_stream_format("output", fs, min(max_num_channels, features["chan_o"]), 24)
                else:
                    dut.set_stream_format("input", fs, features["chan_i"], 24)
                    dut.set_stream_format("output", fs, features["chan_o"], 24)
            else:
                dut._set_full_stream_format(fs, features["chan_i"], 24, features["chan_o"], 24, True) # call low-level function to bypass the 10 channel limit check for 176.4, 192kHz

            print(f"test_loopback_dac: config {config}, fs {fs}")

            with XsigInput(fs, duration, xsig_config_path, dut.dev_name, blocking=True) as xsig_proc:
                pass

            xsig_lines = xsig_proc.proc_output

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += xsig_lines + "\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
