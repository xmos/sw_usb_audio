# Copyright (c) 2024, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
import platform
import mido

from test_midi import (
    input_midi_file_name,
    output_midi_file_name,
    run_midi_test_file
    )

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    AudioAnalyzerHarness,
    wait_for_midi_ports,
    find_xmos_midi_device,
    XrunDut,
    XsigInput,
    XsigOutput,
    xsig_completion_time_s
)
from conftest import list_configs, get_config_features


def midi_stress_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)

    # XTAGs not present
    if not all(xtag_ids):
        return True

    # Until we fix Jenkins user permissions for MIDI on Mac https://xmosjira.atlassian.net/browse/UA-254
    if platform.system() == "Darwin":
        return True

    if features["i2s_loopback"]:
        return True

    if not features["midi"]:
        return True

    return False


def midi_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 10
    return duration


@pytest.mark.uncollect_if(func=midi_stress_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_midi_loopback_stress(pytestconfig, board, config):
    """
    This test streams 8ch audio in/out at 192kHz in order to stress the system and then runs the 
    standard test_midi.py test whilst doing so. Note we only check the xsig input for analog
    (not the harness xscope output) because as soon as you stop either the harness or xsig the 
    other will throw an error due to real-time checking.
    """
    features = get_config_features(board, config)

    xsig_config = f'mc_midi_stress_8ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    fs_audio = max(features["samp_freqs"]) # Highest rate for maximum stress
    with XrunDut(adapter_dut, board, config) as dut:

        # Ensure firmware is up and enumerated as MIDI
        wait_for_midi_ports()

        time_start = time.time()
        with (
            AudioAnalyzerHarness(
                adapter_harness, xscope="io"
            ) as harness,
            # Due to in and out in xsig config this streams audio in both directions for max stress
            XsigInput(fs_audio, duration, xsig_config_path, dut.dev_name, ident=f"midi-stress-{board}-{config}-{fs_audio}") as xsig_proc_in
            ):
            
            with (mido.open_input(find_xmos_midi_device(mido.get_input_names())) as in_port,
                  mido.open_output(find_xmos_midi_device(mido.get_output_names())) as out_port):
            
                # Keep looping midi_test until time up
                while time.time() < time_start + duration + xsig_completion_time_s:
                    run_midi_test_file(input_midi_file_name, output_midi_file_name, in_port, out_port)

        # Stop the harness
        harness.terminate()
        xscope_lines = harness.get_output() # This will always see a loss of signal at the end but useful for debug
        xsig_lines = xsig_proc_in.get_output()

        with open(xsig_config_path) as file:
            xsig_json = json.load(file)

        # xsig outout parsing for D2H streaming
        failures = check_analyzer_output(xsig_lines, xsig_json["in"])
        if len(failures) > 0:
            fail_str += f"Failure at sample rate {fs_audio}\n"
            fail_str += "\n".join(failures) + "\n\n"
            fail_str += f"xscope stdout at sample rate {fs_audio}\n"
            fail_str += "\n".join(xscope_lines) + "\n\n"
            fail_str += f"xsig stdout at sample rate {fs_audio}\n"
            fail_str += "\n".join(xsig_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
