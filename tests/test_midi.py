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
import random

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    XrunDut,
    wait_for_midi_ports,
    find_xmos_midi_device
)
from conftest import list_configs, get_config_features


# This track takes about 0.9s to send across MIDI
input_midi_file_name = 'tools/midifiles/Bach.mid'
output_midi_file_name = 'tools/midifiles/Bach_loopback.mid'


def midi_loopback_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)

    # Until we fix Jenkins user permissions for MIDI on Mac https://xmosjira.atlassian.net/browse/UA-254
    if platform.system() == "Darwin":
        return True

    # Skip loopback
    if features["i2s_loopback"]:
        return True

    # XTAGs not present
    if not all(xtag_ids):
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

def midi_receive_with_timeout(in_port, timeout_s=10):
    for s in range(timeout_s):
        msg = in_port.receive(block=False)
        if msg is not None:
            return msg

    pytest.fail(f"MIDI receive message failed after {timeout_s}s.")

def run_sysex_message(in_port, out_port, length=2048):
    print(f"Testing sysex message of {length} bytes")
    payload = [random.randrange(0, 128, 1) for i in range(length)]
    ref_msg = mido.Message('sysex', data=payload)

    t0 = time.time()
    out_port.send(ref_msg)
    t1 = time.time()

    elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
    bytes_per_second = length / elapsed
    print(f"Sending took: {t1-t0:.2f}s for {length} B midi sysex message ({bytes_per_second:.2f} B/s)")

    t0 = time.time()
    dut_msg = midi_receive_with_timeout(in_port)
    t1 = time.time()
    elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
    bytes_per_second = length / elapsed
    print(f"Receiving took: {t1-t0:.2f}s for {length} B midi sysex message ({bytes_per_second:.2f} B/s)")

    assert ref_msg.bytes() == dut_msg.bytes()

def run_midi_test_file(input_midi_file_name, output_midi_file_name, in_port, out_port):
    print(f"Testing MIDI loopback of file {input_midi_file_name}")

    midi_file_in = mido.MidiFile(input_midi_file_name)
    midi_file_out = mido.MidiFile()

    # Send each track in the file
    for i, track in enumerate(midi_file_in.tracks):
        print(f'Found track {i}: {track.name}')

        output_track = mido.MidiTrack()
        midi_file_out.tracks.append(track)

        # Send MIDI file at full speed (heavily uses H2D firmware FIFO)
        msg_count = 0
        t0 = time.time()
        for msg in track:
            if msg.is_meta:
                # print("Meta message: ", msg)
                continue
            else:
                # print("Sent:", msg)
                out_port.send(msg)
                msg_count += 1

        t1 = time.time()
        usb_msg_size = 4
        elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
        bytes_per_second = usb_msg_size * msg_count / elapsed
        print(f"Sending took: {t1-t0:.2f}s for {msg_count} midi messages ({bytes_per_second:.2f} B/s)")

        # Receive MIDI files (will be throttled to 3125Bps by UART)
        t0 = time.time()
        for msg_num in range(msg_count):
            msg_in = midi_receive_with_timeout(in_port)
            # print("Received:", msg_in)

            output_track.append(msg_in)
        t1 = time.time()

        elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
        bytes_per_second = usb_msg_size * msg_count / elapsed
        print(f"Receiving took: {t1-t0:.2f}s for {msg_count} midi messages ({bytes_per_second:.2f} B/s)")

        # We know that the MIDI file will have completed looping back at this point so OK to iterate

    # Save received file
    midi_file_out.save(output_midi_file_name)

    # Do binary diff on files
    assert filecmp.cmp(input_midi_file_name, output_midi_file_name), "MIDI Test failed - diff between input and output files"

@pytest.mark.uncollect_if(func=midi_loopback_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_midi_loopback(pytestconfig, board, config):

    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])

    time_start = time.time()

    with XrunDut(adapter_dut, board, config, timeout=120) as dut:
        wait_for_midi_ports(timeout_s=60)
        with (mido.open_input(find_xmos_midi_device(mido.get_input_names())) as in_port,
              mido.open_output(find_xmos_midi_device(mido.get_output_names())) as out_port):

            # Keep looping test until time up
            while time.time() < time_start + duration:
                run_midi_test_file(input_midi_file_name, output_midi_file_name, in_port, out_port)
                max_sysex_length = 3092
                run_sysex_message(in_port, out_port, length=random.randrange(1, max_sysex_length + 1, 1))
