# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
import io
from pathlib import Path
import pytest
import sh
import time
import json
import tempfile

import os
import pprint

from usb_audio_test_utils import (wait_for_portaudio, get_firmware_path_harness,
    get_firmware_path, mark_tests, check_analyzer_output)


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, xsig config)
analogue_input_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ('xk_216_mc', '2i10o10xxxxxx',         192000, 10, "mc_analogue_input_8ch.json")
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        ('xk_216_mc', '1i2o2xxxxxx',             44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '1i2o2xxxxxx',             48000, 600, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',         44100, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   44100, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',          192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               192000, 600, "mc_analogue_input_2ch.json")
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        ('xk_216_mc', '1i2o2xxxxxx',             44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '1i2o2xxxxxx',             48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',         48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',         88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',         96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',   96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',     96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    192000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',      48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxd',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '1i2o2',                48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                88200, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                96000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               176400, 1800, "mc_analogue_input_2ch.json")
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "xsig_config"], analogue_input_configs)
def test_analogue_input(xtagctl_wrapper, xsig, board, config, fs, duration, xsig_config):
    env_var = os.environ
    print('environment variables')
    pprint.pprint(dict(env_var), width=1)

    xsig_config_path = Path(__file__).parent / 'xsig_configs' / xsig_config
    adapter_dut, adapter_harness = xtagctl_wrapper

    # xrun the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    sh.xrun("--adapter-id", adapter_harness, harness_firmware)
    # xflash the firmware
    firmware = get_firmware_path(board, config)
    sh.xrun("--adapter-id", adapter_dut, firmware)

    wait_for_portaudio(board, config)

    # Run xsig
    xsig_output = sh.Command(xsig)(fs, duration * 1000, xsig_config_path, _err_to_out=True)
    xsig_lines = xsig_output.splitlines()

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json['in'])


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, xsig config)
analogue_output_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ('xk_216_mc', '1i2o2xxxxxx',            48000, 10, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',        96000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  48000, 10, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  96000, 10, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i10o10xxxxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',    192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',               48000, 10, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               48000, 10, "mc_analogue_output_2ch.json")
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        ('xk_216_mc', '1i2o2xxxxxx',            44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '1i2o2xxxxxx',            48000, 600, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',        44100, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  44100, 600, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i10o10xxxxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',               44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',              192000, 600, "mc_analogue_output_2ch.json")
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        ('xk_216_mc', '1i2o2xxxxxx',            44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '1i2o2xxxxxx',            48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',        48000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',        88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8',        96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  48000, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  88200, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i8o8xxxxx_tdm8_slave',  96000, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2i10o10xxxxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    48000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',    96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xxxxxx_slave',   192000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10msxxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',     96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xsxxxx_mix8',    176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2i10o10xssxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',               44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '1i2o2',               48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               88200, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               96000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',              176400, 1800, "mc_analogue_output_2ch.json")
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "xsig_config"], analogue_output_configs)
def test_analogue_output(xtagctl_wrapper, xsig, board, config, fs, duration, xsig_config):
    xsig_config_path = Path(__file__).parent / 'xsig_configs' / xsig_config
    adapter_dut, adapter_harness = xtagctl_wrapper

    # xrun the dut
    firmware = get_firmware_path(board, config)
    sh.xrun("--adapter-id", adapter_dut, firmware)

    wait_for_portaudio(board, config)

    # xrun --xscope the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    xscope_out = io.StringIO()
    harness_xrun = sh.xrun(
        "--adapter-id",
        adapter_harness,
        "--xscope",
        harness_firmware,
        _out=xscope_out,
        _err_to_out=True,
        _bg=True,
        _bg_exc=False,
    )

    # Run xsig for duration + 2 seconds
    xsig_cmd = sh.Command(xsig)(fs, (duration + 2) * 1000, xsig_config_path, _bg=True)
    time.sleep(duration)
    # Get analyser output
    try:
        harness_xrun.kill_group()
        harness_xrun.wait()
    except sh.SignalException:
        # Killed
        pass
    xscope_str = xscope_out.getvalue()
    xscope_lines = xscope_str.split("\n")

    # Wait for xsig to exit (timeout after 5 seconds)
    xsig_cmd.wait(timeout=5)

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xscope_lines, xsig_json['out'])
