# Copyright (c) 2024, XMOS Ltd, All rights reserved
import pytest
import time
import mido
import filecmp
import random
import platform

from usb_audio_test_utils import (
    get_xtag_dut,
    XrunDut,
    wait_for_midi_ports,
    find_xmos_midi_device
)
from conftest import list_configs, get_config_features


# This track takes about 0.9s to send across MIDI
input_midi_file_name = 'tools/midifiles/Bach.mid'
output_midi_file_name = 'tools/midifiles/Bach_loopback.mid'


midi_loopback_smoke_configs = [
    ("xk_316_mc", "2AMi18o18mssaax"),
]

def midi_loopback_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    xtag_id = get_xtag_dut(pytestconfig, board)

    # Skip loopback
    if features["i2s_loopback"]:
        return True

    # XTAGs not present
    if not xtag_id:
        return True

    if not features["midi"]:
        return True

    if (
        pytestconfig.getoption("level") == "smoke"
        and (board, config) not in midi_loopback_smoke_configs
    ):
        return True

    return False


def midi_duration(level, partial):
    return 10
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration

def midi_receive_with_timeout(in_port, timeout_s=10, fail_on_timeout=True):
    time_start = time.time()
    while(time.time() < time_start + timeout_s):
        msg = in_port.receive(block=False)
        if msg is not None:
            return msg
        #print("midi rx no msg yet")
        time.sleep(0.1)

    if fail_on_timeout:
        pytest.fail(f"MIDI receive message failed after {timeout_s}s.")
    else:
        return None

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
                #print("Meta message: ", msg)
                continue
            else:
                #print("Sent:", msg)
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
    print(f"*** starting test_midi_loopback {board} {config}")

    features = get_config_features(board, config)

    adapter_dut = get_xtag_dut(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])

    test_pass = 0
    if platform.system() == "Windows":
        midi_port_wait_timeout = 60
    else:
        midi_port_wait_timeout = 10
    for i in range(6):
        print(f"ITER {i}")
        with XrunDut(adapter_dut, board, config, timeout=120):
            ret = wait_for_midi_ports(timeout_s=midi_port_wait_timeout)
            if ret:
                continue
            else:
                with (mido.open_input(find_xmos_midi_device(mido.get_input_names())) as in_port,
                    mido.open_output(find_xmos_midi_device(mido.get_output_names())) as out_port):
                    while True: # receive the first few messages that only seem to arrive when testing on MacOs
                        dut_msg = midi_receive_with_timeout(in_port, fail_on_timeout=False)
                        if dut_msg is None:
                            break
                    time_start = time.time()

                    max_sysex_length = 1022 # test only works for sysex payload <= 1022
                    # Keep looping test until time up
                    while time.time() < time_start + duration:
                        run_midi_test_file(input_midi_file_name, output_midi_file_name, in_port, out_port)
                        run_sysex_message(in_port, out_port, length=random.randrange(1, max_sysex_length + 1, 1))
                    run_sysex_message(in_port, out_port, length=max_sysex_length) # make sure we test the largest supported size
                    test_pass = 1
                    break
    if test_pass == 0:
        pytest.fail(f"No XMOS MIDI ports found after multiple tries: {mido.get_input_names()}, {mido.get_output_names()}")

