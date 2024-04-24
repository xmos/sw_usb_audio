# Copyright (c) 2024, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features

def midi_common_uncollect(features, board, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if features["i2s_loopback"]:
        return True
    return False


def midi_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["midi"], midi_common_uncollect(features, board, pytestconfig)]
    )


def midi_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 10
    return duration


@pytest.mark.uncollect_if(func=midi_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_midi_loopback_stress(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_midi_stress_8ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    fs_audio = [features["samp_freqs"][-1]] # Highest rate
    with XrunDut(adapter_dut, board, config) as dut:
            with (
                AudioAnalyzerHarness(
                    adapter_harness, xscope="io"
                ) as harness,
                XsigOutput(fs_audio, None, xsig_config_path, dut.dev_name),
            ):
                
                # DO MIDI TEST HERE
                time.sleep(duration)


                harness.terminate()
                xscope_lines = harness.get_output()

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xscope_lines, xsig_json["out"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs_audio}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xscope stdout at sample rate {fs_audio}\n"
                fail_str += "\n".join(xscope_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
