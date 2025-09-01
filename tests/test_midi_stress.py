# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
from pathlib import Path
import pytest
import time
import json
import mido
import platform


from test_midi import (
    run_midi_seq_id
    )

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.AudioAnalyzerHarness import AudioAnalyzerHarness
from hardware_test_tools.Xsig import XsigInput
from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut_and_harness


xsig_completion_time_s = 6

def midi_stress_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)

    if pytestconfig.getoption("level") == "smoke":
        # Don't run MIDI stress at smoke level
        return True

    # XTAGs not present
    if not all(xtag_ids):
        return True

    if features["i2s_loopback"]:
        return True

    if not features["midi"]:
        return True

    return False


def midi_stress_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
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
    if config.startswith("1") and platform.system() == "Windows":
        pytest.xfail("UAC1.0 when running with Windows builtin MIDI driver has issues.")

    print(f"*** starting test_midi_loopback_stress:  {board} {config}")

    send_delay = pytestconfig.getoption("midi_send_delay")
    print(f"midi_send_delay = {send_delay} seconds")

    features = get_config_features(board, config)

    xsig_config = f'mc_midi_stress_{features["analogue_i"]}ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = midi_stress_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    fs_audio = max(features["samp_freqs"]) # Highest rate for maximum stress
    if platform.system() == "Windows":
        midi_port_wait_timeout = 60
        num_restarts = 1
    else:
        midi_port_wait_timeout = 10
        num_restarts = 3

    log_file_name = f"midi_stress_{board}_{config}"
    with AppUsbAudDut(adapter_dut, board, config) as dut:

        dut.set_stream_format("input", fs_audio, features["chan_i"], 24)
        dut.set_stream_format("output", fs_audio, features["chan_o"], 24)

        # Ensure firmware is up and enumerated as MIDI
        ret = dut.wait_for_midi_ports(timeout_s=midi_port_wait_timeout, restart_attempts=num_restarts)
        if not ret:
            pytest.fail(f"No XMOS MIDI ports found after multiple tries: {mido.get_input_names()}, {mido.get_output_names()}")

        with (
            AudioAnalyzerHarness(
                adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer",
            ) as harness,
            XsigInput(fs_audio, duration, xsig_config_path, dut.dev_name, ident=f"midi-stress-{board}-{config}-{fs_audio}") as xsig_proc_in
        ):

            with (mido.open_input(dut.midi_in) as in_port,
                mido.open_output(dut.midi_out) as out_port):
                print("*** Looping test_midi_loopback_stress....")
                time_start = time.time()

                # Keep looping midi_test until time up
                while time.time() < time_start + duration + xsig_completion_time_s + 10:
                    run_midi_seq_id(in_port, out_port, send_delay_s=send_delay, log_file_name=log_file_name)

        xsig_lines = xsig_proc_in.proc_output

        with open(xsig_config_path) as file:
            xsig_json = json.load(file)

        # xsig outout parsing for D2H streaming
        failures = check_analyzer_output(xsig_lines, xsig_json["in"])
        if len(failures) > 0:
            fail_str += f"Failure at sample rate {fs_audio}\n"
            fail_str += "\n".join(failures) + "\n\n"
            fail_str += f"xsig stdout at sample rate {fs_audio}\n"
            fail_str += xsig_lines + "\n"
            pytest.fail(fail_str)
