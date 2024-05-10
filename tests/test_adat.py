# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    AudioAnalyzerHarness,
    XrunDut,
    XsigOutput,
)
from conftest import list_configs, get_config_features

def adat_common_uncollect(features, board, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if features["i2s_loopback"]:
        return True
    return False


def adat_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["adat_i"], adat_common_uncollect(features, board, pytestconfig)]
    )


def adat_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["adat_o"], adat_common_uncollect(features, board, pytestconfig)]
    )


def adat_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 10
    return duration


@pytest.mark.uncollect_if(func=adat_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_adat_output(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_digital_output_{features["analogue_o"]}ch_adat'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = adat_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    fs_adat = [fs for fs in features["samp_freqs"] if fs <= 48000]
    with XrunDut(adapter_dut, board, config) as dut:
        for fs in fs_adat:
            dut.set_stream_format("output", fs, features["chan_o"], 24)
            with (
                AudioAnalyzerHarness(
                    adapter_harness, config="adat_test", xscope="io"
                ) as harness,
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
