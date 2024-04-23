# Copyright (c) 2024, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
import platform
import mido
import time
import filecmp

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    XrunDut,
)
from conftest import list_configs, get_config_features

def midi_common_uncollect(features, board, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)

    # Skip loopback
    if features["i2s_loopback"]:
        return True

    # XTAGs not present
    if not all(xtag_ids):
        return True
    return False


def midi_loopback_uncollect(pytestconfig, board, config):
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


def find_xmos_midi_device(devices):
    for device in devices:
        if "XMOS" in device:
            return device

    return None


@pytest.mark.uncollect_if(func=midi_loopback_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_midi_loopback(pytestconfig, board, config):

    input_midi_file_name = 'tools/midifiles/Bach.mid'
    output_midi_file_name = 'tools/midifiles/Bach_loopback.mid'

    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        midi_file_in = mido.MidiFile(input_midi_file_name)
        midi_file_out = mido.MidiFile()

        in_port = mido.open_input(find_xmos_midi_device(mido.get_input_names()))
        out_port = mido.open_output(find_xmos_midi_device(mido.get_output_names()))


        for i, track in enumerate(midi_file_in.tracks):
            print(f'Found track {i}: {track.name}')

            output_track = mido.MidiTrack()
            midi_file_out.tracks.append(track)

            # Send MIDI file at full speed (checks input FIFO)
            msg_count = 0
            t0 = time.time()
            for msg in track:
                if msg.is_meta:
                    print("Meta message: ", msg)
                    continue
                else:
                    # print("Sent:", msg)
                    out_port.send(msg)
                    msg_count += 1

            t1 = time.time()
            usb_msg_size = 4
            bytes_per_second = usb_msg_size * msg_count / (t1 - t0)
            print(f"Sending took: {t1-t0} for {msg_count} midi messages ({bytes_per_second:.2f} B/s)")

            # Receive MIDI files (will be throttled to 3125Bps by UART)
            t0 = time.time()
            for msg_num in range(msg_count):
                msg_in = in_port.receive()
                # print("Received:", msg_in)

                output_track.append(msg_in)
            t1 = time.time()

            bytes_per_second = usb_msg_size * msg_count / (t1 - t0)
            print(f"Receiving took: {t1-t0} for {msg_count} messages ({bytes_per_second:.2f} B/s)")


        midi_file_out.save(output_midi_file_name)
        
        # Do binary diff
        assert filecmp.cmp(input_midi_file_name, output_midi_file_name)

