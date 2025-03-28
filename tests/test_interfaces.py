# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
import pytest

from conftest import get_config_features, AppUsbAudDut, get_xtag_dut


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
    ("xk_316_mc", "2AMi16o16xxxaax"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
]


def interface_uncollect(pytestconfig, board, config):
    if pytestconfig.getoption("level") == "smoke":
        # Don't run test_interfaces at smoke level
        return True

    xtag_id = get_xtag_dut(pytestconfig, board)
    # XTAGs not present
    if not xtag_id:
        return True

    return False


@pytest.mark.uncollect_if(func=interface_uncollect)
@pytest.mark.parametrize(["board", "config"], interface_configs)
def test_interfaces(pytestconfig, board, config):
    features = get_config_features(board, config)

    fail_str = ""
    adapter_dut = get_xtag_dut(pytestconfig, board)

    with (AppUsbAudDut(adapter_dut, board, config) as dut):
        for direction in ("input", "output"):
            expected_interfaces = get_expected_interfaces(direction, features)

            for expected_if in expected_interfaces:
                result = dut.set_stream_format(*expected_if, fail_on_err=False)

                if result != 0:
                    fail_str += f"selecting {expected_if} in firmware {config}\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
