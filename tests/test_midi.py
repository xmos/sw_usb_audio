# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
import pytest
import time
import mido
import filecmp
import random
import platform
import subprocess

from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut

# This track takes about 0.9s to send across MIDI
input_midi_file_name = 'tools/midifiles/Bach.mid'

if platform.system() == "Darwin":
    midi_loopback_smoke_configs = [
        ("xk_316_mc", "2AMi18o18mssaax"),
        ("xk_216_mc", "2AMi18o18mssaax")
    ]
else:
    midi_loopback_smoke_configs = []

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
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration

def midi_receive_with_timeout(in_port, timeout_s=10, fail_on_timeout=True):
    """
    Wait for a MIDI message on the given input port.

    Returns the message if received within the timeout; returns None or fails the test
    after `timeout_s` seconds depending on `fail_on_timeout`.
    """
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

    assert ref_msg.bytes() == dut_msg.bytes(), f"sysex msg mismatch:\nout_msg: {ref_msg}\nlooped_back_msg: {dut_msg}"


def check_for_mismatch(expected_msgs, recvd_msgs, log_file_name):
    """
    Compare expected and received MIDI messages.

    Logs both sequences to `exp_<log_file_name>.log` and `recv_<log_file_name>.log`,
    prints mismatches to stdout, and raises an AssertionError if counts or contents differ.
    """
    fail = False
    recvd_msg_count = len(recvd_msgs)
    exp_msg_count = len(expected_msgs)

    print(f"{exp_msg_count} messages sent and {recvd_msg_count} messages received")

    if recvd_msg_count != exp_msg_count:
        print(f"Mismatch in listener's received message count. Expected: {exp_msg_count}, Received: {recvd_msg_count}")
        fail = True

    with open(f"exp_{log_file_name}.log", "w") as f_exp, open(f"recv_{log_file_name}.log", "w") as f_recv:
        check_count = min(recvd_msg_count, exp_msg_count)
        for i in range(check_count):
            expected_msg = expected_msgs[i].copy(time=0) # time would be different between OUT and IN msgs so overwrite it to 0
            received_msg = recvd_msgs[i].copy(time=0)
            f_exp.write(f"{expected_msg}\n")
            f_recv.write(f"{received_msg}\n")
            if(expected_msg != received_msg):
                print(f"Message {i} mismatches: Expected: {expected_msg}, Received: {received_msg}")
                fail = True

        # write any remaining
        for i in range(check_count, exp_msg_count):
            expected_msg = expected_msgs[i].copy(time=0) # time would be different between OUT and IN msgs so overwrite it to 0
            f_exp.write(f"{expected_msg}\n")

        for i in range(check_count, recvd_msg_count):
            received_msg = recvd_msgs[i].copy(time=0)
            f_recv.write(f"{received_msg}\n")

    assert not fail, "midi loopback message mismatch, see printed stdout and log files"

def run_midi_seq_id(in_port, out_port, use_sendmidi=False, send_delay_s=0, log_file_name="midi"):
    """
    Send a sequence of MIDI note_on messages and verify loopback.

    Generates 1000 messages where note and velocity fields together encode a
    sequence ID, making mismatches easier to debug. Messages are sent via
    `mido.send()` or `sendmidi`, received on `in_port`, and compared. Prints
    throughput statistics for sending and receiving.
    """
    msg_count = 1000
    out_msgs = []
    if use_sendmidi:
        sendmidi_cmd_file = "sendmidi_cmds.txt"
        with open(sendmidi_cmd_file, "w") as fp:
            ret = subprocess.run(["sendmidi", "list"], check=True, capture_output=True, text=True)
            assert ret.stdout, "sendmidi list returned no device. Check if sendmidi is installed and the device is connected."
            assert "XMOS" in ret.stdout, f"XMOS device not found in sendmidi list: {ret.stdout}"
            sendmidi_xmos_dev = ret.stdout.strip()
            fp.write(f'dev "{sendmidi_xmos_dev}"\n')
            for i in range(msg_count):
                nt = int(i / 128)
                vel = i % 128
                msg = mido.Message('note_on', note=nt, velocity=vel)
                out_msgs.append(msg)
                fp.write(f'on {nt} {vel}\n')
    else:
        for i in range(msg_count):
            nt = int(i / 128)
            vel = i % 128
            msg = mido.Message('note_on', note=nt, velocity=vel)
            out_msgs.append(msg)

    recvd_msg_count = 0 # looped back message count
    recvd_msgs = []
    t0 = time.time()
    if use_sendmidi:
        cmd = ["sendmidi", "dev", sendmidi_xmos_dev, "file", sendmidi_cmd_file]
        subprocess.run(cmd, check=True)
    else:
        for (msg_num, msg) in enumerate(out_msgs):
            out_port.send(msg)
            time.sleep(send_delay_s)

    t1 = time.time()
    usb_msg_size = 4
    elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
    bytes_per_second = usb_msg_size * msg_count / elapsed
    print(f"Sending took: {t1-t0:.2f}s for {msg_count} midi messages ({bytes_per_second:.2f} B/s)")

    # Receive MIDI files (will be throttled to 3125Bps by UART)
    t0 = time.time()
    for msg_num in range(recvd_msg_count, msg_count):
        msg_in = midi_receive_with_timeout(in_port, fail_on_timeout=False) # dont fail before the check_for_mismatch check
        if msg_in:
            recvd_msgs.append(msg_in)
            recvd_msg_count += 1
        else: # timeout
            break
    t1 = time.time()

    elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
    bytes_per_second = usb_msg_size * recvd_msg_count / elapsed
    print(f"Receiving took: {t1-t0:.2f}s for {recvd_msg_count} midi messages ({bytes_per_second:.2f} B/s)")

    check_for_mismatch(out_msgs, recvd_msgs, log_file_name) # check looped back messages for mismatches


def run_midi_test_file(input_midi_file_name, in_port, out_port, send_delay_s=0, log_file_name="midi"):
    print(f"Testing MIDI loopback of file {input_midi_file_name}")

    midi_file_in = mido.MidiFile(input_midi_file_name)

    # Send each track in the file
    for i, track in enumerate(midi_file_in.tracks):
        print(f'Found track {i}: {track.name}')

        out_msgs = [msg for msg in track if not msg.is_meta]
        msg_count = len(out_msgs)
        print(f"Send track {i} containing {msg_count} messages")

        if not msg_count: # Nothing to send in this track
            continue

        # Send MIDI file at full speed (heavily uses H2D firmware FIFO)
        recvd_msg_count = 0 # looped back message count
        recvd_msgs = []
        t0 = time.time()
        for (msg_num, msg) in enumerate(out_msgs):
            out_port.send(msg)
            time.sleep(send_delay_s)

        t1 = time.time()
        usb_msg_size = 4
        elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
        bytes_per_second = usb_msg_size * msg_count / elapsed
        print(f"Sending took: {t1-t0:.2f}s for {msg_count} midi messages ({bytes_per_second:.2f} B/s)")

        # Receive MIDI files (will be throttled to 3125Bps by UART)
        t0 = time.time()
        for msg_num in range(msg_count):
            msg_in = midi_receive_with_timeout(in_port, fail_on_timeout=False) # dont fail before the check_for_mismatch check
            if msg_in:
                recvd_msgs.append(msg_in)
                recvd_msg_count += 1
            else: # timeout
                break
        t1 = time.time()

        elapsed = (t1 - t0) if (t1 - t0) > 0 else 0.001 # Avoid div by zero
        bytes_per_second = usb_msg_size * recvd_msg_count / elapsed
        print(f"Receiving took: {t1-t0:.2f}s for {recvd_msg_count} midi messages ({bytes_per_second:.2f} B/s)")

        check_for_mismatch(out_msgs, recvd_msgs, log_file_name) # Check looped back messages for mismatches


@pytest.mark.uncollect_if(func=midi_loopback_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_midi_loopback(pytestconfig, board, config):
    if config.startswith("1") and platform.system() == "Windows":
        pytest.xfail("UAC1.0 when running with Windows builtin MIDI driver has issues.")

    random.seed(0)
    print(f"*** starting test_midi_loopback {board} {config}")

    features = get_config_features(board, config)
    use_sendmidi = pytestconfig.getoption("use_sendmidi")
    print(f"use_sendmidi = {use_sendmidi}")
    if use_sendmidi and platform.system() != "Darwin":
        pytest.fail("sendmidi only supported on MacOS")

    send_delay = pytestconfig.getoption("midi_send_delay")
    print(f"midi_send_delay = {send_delay} seconds")

    adapter_dut = get_xtag_dut(pytestconfig, board)
    duration = midi_duration(pytestconfig.getoption("level"), features["partial"])

    if platform.system() == "Windows":
        midi_port_wait_timeout = 60
        num_restarts = 1
    else:
        midi_port_wait_timeout = 10
        num_restarts = 3

    log_file_name = f"midi_{board}_{config}"
    with AppUsbAudDut(adapter_dut, board, config) as dut:
        ret = dut.wait_for_midi_ports(timeout_s=midi_port_wait_timeout, restart_attempts=num_restarts)
        if not ret:
            pytest.fail(f"No XMOS MIDI ports found after multiple tries: {mido.get_input_names()}, {mido.get_output_names()}")

        with (mido.open_input(dut.midi_in) as in_port,
            mido.open_output(dut.midi_out) as out_port):
            while True: # receive the first few messages that only seem to arrive when testing on MacOs
                dut_msg = midi_receive_with_timeout(in_port, fail_on_timeout=False)
                if dut_msg is None:
                    break
            time_start = time.time()

            # Run a sequence ID test to verify basic functionality
            run_midi_seq_id(in_port, out_port, use_sendmidi=use_sendmidi, send_delay_s=send_delay, log_file_name=log_file_name)

            max_sysex_length = 1022 # test only works for sysex payload <= 1022
            # Keep looping test until time up
            while time.time() < time_start + duration:
                run_midi_test_file(input_midi_file_name, in_port, out_port, send_delay_s=send_delay, log_file_name=log_file_name)
                run_sysex_message(in_port, out_port, length=random.randrange(1, max_sysex_length + 1, 1))
            run_sysex_message(in_port, out_port, length=max_sysex_length) # make sure we test the largest supported size

