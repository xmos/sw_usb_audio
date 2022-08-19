# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
import tempfile
import signal

from usb_audio_test_utils import (wait_for_portaudio, get_firmware_path_harness,
    get_firmware_path, run_audio_command, mark_tests, check_analyzer_output,
    get_xscope_port_number, wait_for_xscope_port)


all_freqs = [44100, 48000, 88200, 96000, 176400, 192000]


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration)
spdif_input_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ("xk_216_mc", "2Ai10o10xssxxx",  48000, 10),
        ("xk_216_mc", "2Ai10o10xssxxx", 192000, 10),
        ("xk_316_mc", "2Ai10o10xsxxxx",  44100, 10),
        ("xk_316_mc", "2Ai10o10xsxxxx",  96000, 10),
        ("xk_316_mc", "2Ai10o10xssxxx",  88200, 10),
        ("xk_316_mc", "2Ai10o10xssxxx", 192000, 10)
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        *[("xk_216_mc", "2Ai10o10xssxxx", fs, 600) for fs in all_freqs],
        *[("xk_316_mc", "2Ai10o10xsxxxx", fs, 600) for fs in all_freqs]
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        *[("xk_216_mc", "2Ai10o10xssxxx", fs, 1800) for fs in all_freqs],
        *[("xk_316_mc", "2Ai10o10xsxxxx", fs, 1800) for fs in all_freqs],
        *[("xk_316_mc", "2Ai10o10xssxxx", fs, 1800) for fs in all_freqs]
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration"], spdif_input_configs)
def test_spdif_input(xtag_wrapper, xsig, board, config, fs, duration):
    xsig_config_path = Path(__file__).parent / 'xsig_configs' / "mc_digital_input_8ch.json"
    adapter_dut, adapter_harness = xtag_wrapper

    xscope_port = get_xscope_port_number()

    # Run the harness and set the sample rate for the ramp signal
    harness_firmware = get_firmware_path_harness("xcore200_mc", config="spdif_test")
    harness_proc = subprocess.Popen(["xrun", "--adapter-id", adapter_harness, "--xscope-port", f"localhost:{xscope_port}", harness_firmware],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    wait_for_xscope_port(xscope_port)

    xscope_controller = Path(__file__).parents[2] / "sw_audio_analyzer" / "host_xscope_controller" / "bin_macos" / "xscope_controller"
    subprocess.run([xscope_controller, "localhost", f"{xscope_port}", "0", f"f {fs}"])

    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware])

    wait_for_portaudio(board, config)

    volcontrol_path = Path(__file__).parent / "tools" / "volcontrol" / "volcontrol"
    subprocess.run([volcontrol_path, "--clock", "SPDIF"])

    # Run xsig
    xsig_duration = duration + 5
    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        run_audio_command(out_file, xsig, f"{fs}", f"{duration * 1000}", xsig_config_path)
        time.sleep(xsig_duration)
        out_file.seek(0)
        xsig_lines = out_file.readlines()

    harness_proc.send_signal(signal.SIGINT)

    # Return to using to the internal clock
    subprocess.run([volcontrol_path, "--clock", "Internal"])

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json['in'])


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration)
spdif_output_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ("xk_216_mc", "2Ai10o10msxxxx",        44100, 10),
        ("xk_216_mc", "2Ai10o10xssxxx",       176400, 10),
        ("xk_216_mc", "2Ai10o10xsxxxd",        48000, 10),
        ("xk_216_mc", "2Ai10o10xsxxxx",        48000, 10),
        ("xk_316_mc", "2Ai10o10xxsxxx",        44100, 10),
        ("xk_316_mc", "2Ai10o10xxsxxx",       192000, 10),
        ("xk_316_mc", "2Ai10o10xssxxx",        48000, 10),
        ("xk_316_mc", "2Ai10o10xssxxx",       176400, 10)
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        ("xk_216_mc", "2Ai10o10msxxxx",       192000, 600),
        ("xk_216_mc", "2Ai10o10xssxxx",        48000, 600),
        ("xk_216_mc", "2Ai10o10xssxxx",       176400, 600),
        ("xk_216_mc", "2Ai10o10xsxxxd",       192000, 600),
        ("xk_216_mc", "2Ai10o10xsxxxx",        88200, 600),
        ("xk_216_mc", "2Ai10o10xsxxxx",        96000, 600),
        ("xk_216_mc", "2Ai10o10xsxxxx_mix8",  192000, 600),
        ("xk_316_mc", "2Ai10o10xxsxxx",        44100, 600),
        ("xk_316_mc", "2Ai10o10xxsxxx",        96000, 600),
        ("xk_316_mc", "2Ai10o10xxsxxx",       176400, 600),
        ("xk_316_mc", "2Ai10o10xssxxx",        48000, 600),
        ("xk_316_mc", "2Ai10o10xssxxx",        88200, 600),
        ("xk_316_mc", "2Ai10o10xssxxx",       192000, 600)
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        *[("xk_216_mc", "2Ai10o10msxxxx",       fs, 1800) for fs in all_freqs],
        *[("xk_216_mc", "2Ai10o10xssxxx",       fs, 1800) for fs in all_freqs],
        *[("xk_216_mc", "2Ai10o10xsxxxd",       fs, 1800) for fs in all_freqs],
        *[("xk_216_mc", "2Ai10o10xsxxxx",       fs, 1800) for fs in all_freqs],
        *[("xk_216_mc", "2Ai10o10xsxxxx_mix8",  fs, 1800) for fs in all_freqs],
        *[("xk_316_mc", "2Ai10o10xxsxxx",       fs, 1800) for fs in all_freqs],
        *[("xk_316_mc", "2Ai10o10xssxxx",       fs, 1800) for fs in all_freqs]
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration"], spdif_output_configs)
def test_spdif_output(xtag_wrapper, xsig, board, config, fs, duration):
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_digital_output_8ch.json"
    adapter_dut, adapter_harness = xtag_wrapper

    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware])

    wait_for_portaudio(board, config)

    # Run xsig for longer than the test duration as it will be terminated later
    xsig_duration_ms = (duration + 100) * 1000
    xsig_proc = subprocess.Popen([xsig, f"{fs}", f"{xsig_duration_ms}", xsig_config_path])

    harness_firmware = get_firmware_path_harness("xcore200_mc", config="spdif_test")
    harness_proc = subprocess.Popen(["xrun", "--adapter-id", adapter_harness, "--xscope", harness_firmware],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    time.sleep(duration)

    harness_proc.send_signal(signal.SIGINT)
    xscope_str = harness_proc.stdout.read()
    xscope_lines = xscope_str.splitlines()

    xsig_proc.terminate()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    check_analyzer_output(xscope_lines, xsig_json["out"])
