# Copyright (c) 2024, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import subprocess
import platform

from usb_audio_test_utils import (
    get_xtag_dut_and_harness,
    get_tusb_guid,
    get_volcontrol_path,
    stream_format_setup,
    AudioAnalyzerHarness,
    XrunDut,
)
from conftest import get_config_features


# Determine what interfaces we would expect from the FW
def get_expected_interfaces(direction, features):
    fs = 48000
    if direction == "input":
        if features["adat_i"]:
            interfaces = [  [direction, fs, features["chan_i"] - 0, 24],
                            [direction, fs, features["chan_i"] - 4, 24],
                            [direction, fs, features["chan_i"] - 6, 24] ]
        else:
            interfaces = [  [direction, fs, features["chan_i"], 24]]

    elif direction == "output":
        if features["adat_o"]:
            interfaces = [  [direction, fs, features["chan_o"] - 0, 24],
                            [direction, fs, features["chan_o"] - 4, 24],
                            [direction, fs, features["chan_o"] - 6, 24] ]
        else:
            interfaces = [  [direction, fs, features["chan_o"], 24],
                            [direction, fs, features["chan_o"], 16] ]
    else:
        assert 0, f"Invalid direction sent: {direction}"
    
    return interfaces

# Test cases are defined by a tuple of (board, config)
interface_configs = [
    ("xk_316_mc", "2AMi10o10xssxxx"),
    ("xk_316_mc", "2AMi16o8xxxaxx"),
    ("xk_316_mc", "2AMi8o16xxxxax"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
]


def interface_uncollect(pytestconfig, board, config):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    # if pytestconfig.getoption("level") == "smoke":
    #     return board != "xk_evk_xu316"
    return False


@pytest.mark.uncollect_if(func=interface_uncollect)
@pytest.mark.parametrize(["board", "config"], interface_configs)
def test_interfaces(pytestconfig, board, config):
    features = get_config_features(board, config)
    
    fail_str = ""
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    with (XrunDut(adapter_dut, board, config) as dut):
        for direction in ("input", "output"):
            expected_interfaces = get_expected_interfaces(direction, features)

            for expected_if in expected_interfaces:
                result = dut.stream_format_setup(*expected_if, fail_on_err=False)

                if result != 0:
                    fail_str += f"selecting {expected_if} in firmware {config}\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
