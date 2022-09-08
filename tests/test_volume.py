# Copyright (c) 2022, XMOS Ltd, All rights reserved
import io
from pathlib import Path
import pytest
import time
import json
import subprocess
import re
import signal
import tempfile

from usb_audio_test_utils import (wait_for_portaudio, get_firmware_path_harness,
    get_firmware_path, run_audio_command, mark_tests, check_analyzer_output,
    get_xscope_port_number, wait_for_xscope_port)


class Volcontrol:
    EXECUTABLE = Path(__file__).parent / "tools" / "volcontrol" / "volcontrol"

    def __init__(self, input_output, num_chans, channel=None, master=False):
        self.channel = '0' if master else f'{channel + 1}'
        self.reset_chans = f'{num_chans + 1}'
        self.input_output = input_output

    def reset(self):
        subprocess.run([self.EXECUTABLE, '--resetall', self.reset_chans], check=True)
        # sleep after resetting to allow the analyzer to detect the change
        time.sleep(3)

    def set(self, value):
        subprocess.run([self.EXECUTABLE, '--set', self.input_output, self.channel, f'{value}'],
                       check=True)
        # sleep after setting the volume to allow the analyzer to detect the change
        time.sleep(3)


num_chans = {
    "xk_216_mc": 8,
    "xk_316_mc": 8,
    "xk_evk_xu316": 2,
}


# Test cases are defined by a tuple of (board, config, sample rate, 'm' (master) or channel number)
volume_input_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        *[('xk_216_mc',    '2Ai10o10xxxxxx',        96000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2AMi10o10xxxxxx',       96000, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 48000, ch) for ch in ['m', *range(2)]]
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        *[('xk_216_mc',    '2Ai8o8xxxxx_tdm8',      48000, ch) for ch in ['m', *range(8)]],
        *[('xk_216_mc',    '2Ai10o10msxxxx',       192000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2AMi10o10xxxxxx',       48000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2AMi10o10xsxxxx',      192000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Si10o10xxxxxx',        88200, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 44100, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                 96000, ch) for ch in ['m', *range(2)]]
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        *[('xk_216_mc',    '2Ai10o10xsxxxx_mix8',   44100, ch) for ch in ['m', *range(8)]],
        *[('xk_216_mc',    '2Ai10o10xssxxx',       176400, ch) for ch in ['m', *range(8)]],
        *[('xk_216_mc',    '2Si10o10xxxxxx',       192000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2AMi10o10xxxxxx',       44100, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2AMi10o10xsxxxx',      176400, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2SMi10o10xxxxxx',       96000, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 88200, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                176400, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                192000, ch) for ch in ['m', *range(2)]]
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "channel"], volume_input_configs)
def test_volume_input(xtag_wrapper, xsig, board, config, fs, channel):
    channels = range(num_chans[board]) if channel == "m" else [channel]

    duration = 25

    # Load JSON xsig_config data
    xsig_config = f'mc_analogue_input_{num_chans[board]}ch.json'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    for ch, ch_config in enumerate(xsig_json["in"]):
        if ch in channels:
            xsig_json["in"][ch][0] = "volcheck"

    adapter_dut, adapter_harness = xtag_wrapper

    # xrun the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    subprocess.run(['xrun', '--adapter-id', adapter_harness, harness_firmware], check=True)
    # xflash the firmware
    firmware = get_firmware_path(board, config)
    subprocess.run(['xrun', '--adapter-id', adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    with tempfile.NamedTemporaryFile(mode='w+') as out_file, tempfile.NamedTemporaryFile(mode='w') as xsig_file:
        json.dump(xsig_json, xsig_file)
        xsig_file.flush()

        run_audio_command(out_file, xsig, f"{fs}", f"{duration * 1000}", Path(xsig_file.name))

        time.sleep(5)

        if channel == 'm':
            vol_in = Volcontrol('input', num_chans[board], master=True)
        else:
            vol_in = Volcontrol('input', num_chans[board], channel=int(channel))

        vol_in.reset()
        vol_changes = [0.5, 1.0, 0.75, 1.0]
        for vol_change in vol_changes:
            vol_in.set(vol_change)

        out_file.seek(0)
        xsig_lines = out_file.readlines()

    # Check output
    check_analyzer_output(xsig_lines, xsig_json['in'])


# Test cases are defined by a tuple of (board, config, sample rate, 'm' (master) or channel number)
volume_output_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        *[('xk_216_mc',    '2Ai10o10xxxxxx',        96000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Ai10o10xxxxxx',        96000, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 48000, ch) for ch in ['m', *range(2)]]
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        *[('xk_216_mc',    '2Ai8o8xxxxx_tdm8',      48000, ch) for ch in ['m', *range(8)]],
        *[('xk_216_mc',    '2Ai10o10msxxxx',       192000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Ai10o10xxxxxx',        48000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Ai10o10xsxxxx',       192000, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Si10o10xxxxxx',        88200, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 44100, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                 96000, ch) for ch in ['m', *range(2)]]
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        *[('xk_216_mc',    '2Ai10o10xsxxxx_mix8',   44100, ch) for ch in ['m', *range(8)]],
        *[('xk_216_mc',    '2Ai10o10xssxxx',       176400, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Ai10o10xxxxxx',        44100, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Ai10o10xsxxxx',       176400, ch) for ch in ['m', *range(8)]],
        *[('xk_316_mc',    '2Si10o10xxxxxx',        96000, ch) for ch in ['m', *range(8)]],
        *[('xk_evk_xu316', '2i2o2',                 88200, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                176400, ch) for ch in ['m', *range(2)]],
        *[('xk_evk_xu316', '2i2o2',                192000, ch) for ch in ['m', *range(2)]]
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "channel"], volume_output_configs)
def test_volume_output(xtag_wrapper, xsig, board, config, fs, channel):
    channels = range(num_chans[board]) if channel == "m" else [channel]

    xsig_config = f'mc_analogue_output_{num_chans[board]}ch.json'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config

    adapter_dut, adapter_harness = xtag_wrapper

    # xrun the dut
    firmware = get_firmware_path(board, config)
    subprocess.run(['xrun', '--adapter-id', adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    # Run for long duration to outlast the volume changes; xsig is terminated before it completes
    duration = 100
    xsig_proc = subprocess.Popen([xsig, f'{fs}', f'{duration * 1000}', xsig_config_path])

    xscope_port = get_xscope_port_number()

    # xrun the harness
    harness_firmware = get_firmware_path_harness('xcore200_mc')
    harness_proc = subprocess.Popen(['xrun', '--adapter-id', adapter_harness, '--xscope-port', f'localhost:{xscope_port}', harness_firmware],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    wait_for_xscope_port(xscope_port)

    # Set the channels being tested to 'volume' mode on the analyzer
    analyser_cmds = [f'm {ch} v' for ch in channels]
    xscope_controller = Path(__file__).parents[2] / "sw_audio_analyzer" / "host_xscope_controller" / "bin_macos" / "xscope_controller"
    subprocess.run([xscope_controller, "localhost", f'{xscope_port}', "0", *analyser_cmds], check=True)

    time.sleep(2)

    if channel == "m":
        vol_out = Volcontrol("output", num_chans[board], master=True)
    else:
        vol_out = Volcontrol("output", num_chans[board], channel=channel)

    vol_out.reset()
    vol_changes = [0.5, 1.0, 0.75, 1.0]
    for vol_change in vol_changes:
        vol_out.set(vol_change)

    harness_proc.send_signal(signal.SIGINT)
    xsig_proc.terminate()

    xscope_str = harness_proc.stdout.read()
    xscope_lines = xscope_str.splitlines()

    # Load JSON xsig config data
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    for ch, ch_config in enumerate(xsig_json["out"]):
        if ch in channels:
            xsig_json["out"][ch][0] = "volcheck"

    check_analyzer_output(xscope_lines, xsig_json["out"])
