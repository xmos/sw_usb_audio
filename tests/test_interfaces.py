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


class interface_control:
    def __init__(self):
        self.cmd = [get_volcontrol_path()]
        if platform.system() == "Windows":
            self.cmd.append(f"-g{get_tusb_guid()}")

    def set(self, input_output, num_chans, bit_depth):
        cmd = self.cmd + ["--set-format", input_output, str(num_chans), str(value)]
        result = subprocess.run(
            cmd,
            check=True,
            timeout=10,
        )

        return result.returncode

# Determine what interfaces we would expect from the FW
def get_expected_interfaces(direction, features):
    if direction == "input":
        if "adat_i" in features:
            interfaces = [  [direction, features["chan_i"] - 0, 24],
                            [direction, features["chan_i"] - 4, 24],
                            [direction, features["chan_i"] - 6, 24] ]
        else:
            interfaces = [  [direction, features["chan_i"], 24],
                            [direction, features["chan_i"], 16] ]

    elif direction == "output":
        if "adat_o" in features:
            interfaces = [  [direction, features["chan_o"] - 0, 24],
                            [direction, features["chan_o"] - 4, 24],
                            [direction, features["chan_o"] - 6, 24] ]
        else:
            interfaces = [  [direction, features["chan_o"], 24]]
    else:
        assert 0, f"Invalid direction sent: {direction}"
    
    return interfaces

# Test cases are defined by a tuple of (board, config)
interface_configs = [
    ("xk_316_mc", "2AMi10o10xssxxx"),
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

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness),
    ):
        for direction in ("input", "output"):
            expected_interfaces = get_expected_interfaces(direction, features)

            stream_format_setup("input", fs, features["chan_i"], 24)

            if_ctrl = interface_control()
            for expected_if in expected_interfaces:
                result = if_ctrl.set(*expected_interface)

                if result != 0:
                    fail_str += f"Failure selecting: {expected_if} in firmware: {config}\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
