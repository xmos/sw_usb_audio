# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
import io
from pathlib import Path
import pytest
import subprocess
import time
import json
import tempfile
import signal

from usb_audio_test_utils import (wait_for_portaudio, get_firmware_path_harness,
    get_firmware_path, run_audio_command, mark_tests, check_analyzer_output)


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, xsig config)
analogue_input_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ('xk_216_mc', '1Ai2o2xxxxxx',            48000, 10, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        96000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  48000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  96000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',         192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',   192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',         192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',    192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',         192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',         192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',           48000, 10, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',           96000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx_tdm8',      96000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx_tdm8',      96000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',         192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',          192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2SSi8o8xxxxxx',          192000, 10, "mc_analogue_input_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                48000, 10, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                48000, 10, "mc_analogue_input_2ch.json"),
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        ('xk_216_mc', '1Ai2o2xxxxxx',             44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '1Ai2o2xxxxxx',             48000, 600, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',         44100, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',   44100, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',      48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',          192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',          192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',            44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',            48000, 600, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',           192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',           48000, 600, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx',           192000, 600, "mc_analogue_input_8ch.json"),
        ('xk_evk_xu316',  '1i2o2',                44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316',  '2i2o2',                44100, 600, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316',  '2i2o2',               192000, 600, "mc_analogue_input_2ch.json"),
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        ('xk_216_mc', '1Ai2o2xxxxxx',             44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '1Ai2o2xxxxxx',             48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',         48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',         88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',         96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',   48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',   88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',   96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',     44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',     48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',     88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',     96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    192000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',      44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',      48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',      96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',     176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',      48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',           44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxd',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',           44110, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',           48000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',          176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_216_mc', '2Si10o10xxxxxx',          192000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',            44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',            48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',            44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',            48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',           176400, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',           192000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',           88200, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',           96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',            44100, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',            96000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_316_mc', '2SSi8o8xxxxxx',           192000, 1800, "mc_analogue_input_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                 44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '1i2o2',                 48000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                 44100, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                 88200, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                 96000, 1800, "mc_analogue_input_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                176400, 1800, "mc_analogue_input_2ch.json"),
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "xsig_config"], analogue_input_configs)
def test_analogue_input(xtag_wrapper, xsig, board, config, fs, duration, xsig_config):
    xsig_config_path = Path(__file__).parent / 'xsig_configs' / xsig_config
    adapter_dut, adapter_harness = xtag_wrapper

    # xrun the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    subprocess.run(["xrun", "--adapter-id", adapter_harness, harness_firmware], check=True)
    # xflash the firmware
    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    # Run xsig
    xsig_duration = duration + 5
    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        run_audio_command(out_file, xsig, f"{fs}", f"{duration * 1000}", xsig_config_path)
        time.sleep(xsig_duration)
        out_file.seek(0)
        xsig_lines = out_file.readlines()

    # Harness is still running, so break in with xgdb to stop it
    subprocess.check_output(["xgdb", f"--eval-command=connect --adapter-id {adapter_harness}", "--eval-command=quit"])

    # Check output
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xsig_lines, xsig_json['in'])


# Test cases are defined by a tuple of (board, config, sample rate, seconds duration, xsig config)
analogue_output_configs = [
    # smoke level tests
    *mark_tests(pytest.mark.smoke, [
        ('xk_216_mc', '1Ai2o2xxxxxx',            48000, 10, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        96000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  48000, 10, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  96000, 10, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',   192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',    192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',           48000, 10, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',           96000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx_tdm8',      96000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx_tdm8',      96000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',         192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',          192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx',          192000, 10, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                48000, 10, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                48000, 10, "mc_analogue_output_2ch.json"),
    ]),

    # nightly level tests
    *mark_tests(pytest.mark.nightly, [
        ('xk_216_mc', '1Ai2o2xxxxxx',            44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '1Ai2o2xxxxxx',            48000, 600, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        44100, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  44100, 600, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',   192000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',     48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',           44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',           48000, 600, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',          192000, 600, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi10o8xsxxxx',          48000, 600, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx',          192000, 600, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                44100, 600, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               192000, 600, "mc_analogue_output_2ch.json"),
    ]),

    # weekend level tests
    *mark_tests(pytest.mark.weekend, [
        ('xk_216_mc', '1Ai2o2xxxxxx',            44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '1Ai2o2xxxxxx',            48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        48000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8',        96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  48000, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  88200, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai8o8xxxxx_tdm8_slave',  96000, 1800, "mc_analogue_output_8ch_paired.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    48000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',    96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',   176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xxxxxx_slave',   192000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10msxxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',     44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',     88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',     96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xsxxxx_mix8',    176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',          44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',          88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',          96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_216_mc', '2Ai10o10xssxxx',         176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',           44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '1AMi2o2xxxxxx',           48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',           44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '1SMi2o2xxxxxx',           48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',        176400, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi8o8xxxxxx',          192000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi8o8xsxxxx',           88200, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2AMi8o8xsxxxx',           96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',           44100, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2SMi8o8xxxxxx',           96000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_316_mc', '2ASi8o8xxxxxx',          192000, 1800, "mc_analogue_output_8ch.json"),
        ('xk_evk_xu316', '1i2o2',                44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '1i2o2',                48000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                44100, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                88200, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',                96000, 1800, "mc_analogue_output_2ch.json"),
        ('xk_evk_xu316', '2i2o2',               176400, 1800, "mc_analogue_output_2ch.json"),
    ])
]


@pytest.mark.parametrize(["board", "config", "fs", "duration", "xsig_config"], analogue_output_configs)
def test_analogue_output(xtag_wrapper, xsig, board, config, fs, duration, xsig_config):
    xsig_config_path = Path(__file__).parent / 'xsig_configs' / xsig_config
    adapter_dut, adapter_harness = xtag_wrapper

    # xrun the dut
    firmware = get_firmware_path(board, config)
    subprocess.run(["xrun", "--adapter-id", adapter_dut, firmware], check=True)

    wait_for_portaudio(board, config)

    # xrun --xscope the harness
    harness_firmware = get_firmware_path_harness("xcore200_mc")
    harness_proc = subprocess.Popen(["xrun", "--adapter-id", adapter_harness, "--xscope", harness_firmware],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Run xsig for duration + 2 seconds
    xsig_proc = subprocess.Popen([xsig, f"{fs}", f"{(duration + 2) * 1000}", xsig_config_path])
    time.sleep(duration)

    harness_proc.send_signal(signal.SIGINT)
    xsig_proc.terminate()

    xscope_str = harness_proc.stdout.read()
    xscope_lines = xscope_str.splitlines()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    check_analyzer_output(xscope_lines, xsig_json['out'])
