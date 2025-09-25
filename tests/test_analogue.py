# Copyright 2015-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
from pathlib import Path
import pytest
import time
import json
import platform

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.AudioAnalyzerHarness import AudioAnalyzerHarness
from hardware_test_tools.Xsig import XsigInput, XsigOutput
from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut_and_harness

analogue_smoke_configs = [
    ("xk_216_mc", "2AMi18o18mssaax"),
    ("xk_216_mc", "2ASi10o10xssxxx"),
    ("xk_evk_xu316", "1AMi2o2xxxxxx"),
]

def analogue_require_dut_and_harness(features, board, config, pytestconfig):
    # XTAGs not present
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    if not all(xtag_ids):
        return True
    return False


def analogue_common_uncollect(features, board, config, pytestconfig):
    level = pytestconfig.getoption("level")
    if level == "smoke" and (board, config) not in analogue_smoke_configs:
        return True
    if analogue_require_dut_and_harness(features, board, config, pytestconfig):
        return True
    if features["i2s_loopback"]:
        return True
    return False


def analogue_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    if analogue_common_uncollect(features, board, config, pytestconfig):
        return True
    if not features["analogue_i"]:
        # No input channels
        return True
    return False


def analogue_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    if analogue_common_uncollect(features, board, config, pytestconfig):
        return True
    if not features["analogue_o"]:
        # No output channels
        return True
    return False

def analogue_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration

@pytest.mark.uncollect_if(func=analogue_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_analogue_input_{features["analogue_i"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = (
            "mc_analogue_input_4ch"  # Requires jumper change to test > 4 channels
        )
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    short_test = features["partial"] or board == "xk_316_mc"
    duration = analogue_duration(pytestconfig.getoption("level"), short_test)
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        # Run the analyser using `xrun --xscope-port`, and re-purpose the smux command from the host
        # to synchronize startup — this ensures the analyser is running before we proceed.
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])

        for fs in features["samp_freqs"]:
            print(f"analogue_input: config {config}, fs {fs}")
            if not features["hibw"]:
                if fs > 96000:
                    max_num_channels = 10
                    dut.set_stream_format("input", fs, min(max_num_channels, features["chan_i"]), 24)
                else:
                    dut.set_stream_format("input", fs, features["chan_i"], 24)
            else:
                dut._set_full_stream_format(fs, features["chan_i"], 24, features["chan_i"], 24, True) # call low-level function to bypass the 10 channel limit check for 176.4, 192kHz

            with XsigInput(fs, duration, xsig_config_path, dut.dev_name, ident=f"analogue_input-{board}-{config}-{fs}", blocking=True) as xsig_proc:
                pass # Nothing to do here. XsigInput is run in blocking mode

            xsig_lines = xsig_proc.proc_output
            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += xsig_lines + "\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=analogue_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_analogue_output(pytestconfig, board, config):
    features_tmp = get_config_features(board, config)
    features = features_tmp.copy()

    xsig_config = f'mc_analogue_output_{features["analogue_o"]}ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = "mc_analogue_output_2ch"
    elif board == "xk_216_mc" and features["tdm8"] and features["i2s"] == "S":
        xsig_config += "_paired"  # Pairs of channels can be swapped in hardware
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    short_test = features["partial"] or board == "xk_316_mc"
    duration = analogue_duration(pytestconfig.getoption("level"), short_test)
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            # Issue 120
            if (
                platform.system() == "Windows"
                and board == "xk_316_mc"
                and config == "2AMi8o8xxxxxx_winbuiltin"
                and fs in [44100, 48000]
            ):
                continue

            if not features["hibw"]:
                if fs > 96000:
                    max_num_channels = 10
                    dut.set_stream_format("output", fs, min(max_num_channels, features["chan_o"]), 24)
                else:
                    dut.set_stream_format("output", fs, features["chan_o"], 24)
            else:
                dut._set_full_stream_format(fs, features["chan_i"], 24, features["chan_i"], 24, True) # call low-level function to bypass the 10 channel limit check for 176.4, 192kHz

            print(f"analogue_output: config {config}, fs {fs}")

            with (
                AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
            ):
                # Run the analyser using `xrun --xscope-port`, and override the smux command from the host
                # to synchronize startup — this ensures the analyser is running before we proceed.
                ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
                time.sleep(2)

                with(XsigOutput(fs, 0, xsig_config_path, dut.dev_name) as xsig_proc):
                    time.sleep(duration)
                    harness.terminate()
                    xscope_lines = harness.proc_stdout + harness.proc_stderr

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xscope_lines, xsig_json["out"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xscope stdout at sample rate {fs}\n"
                fail_str += ctrl_out + ctrl_err + xscope_lines + "\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += xsig_proc.proc_output + "\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
