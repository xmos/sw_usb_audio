# Copyright 2022-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
from pathlib import Path
import pytest
import time
import json
import tempfile

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.AudioAnalyzerHarness import AudioAnalyzerHarness
from hardware_test_tools.Xsig import XsigInput, XsigOutput
from conftest import get_config_features, AppUsbAudDut, get_xtag_dut_and_harness


# Test cases are defined by a tuple of (board, config)
volume_configs = [
    ("xk_316_mc", "2AMi10o10xssxxx"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
    ("xk_316_mc", "2AMi32o32xxxxxx_tdm8_mix8_hibw"),
    ("xk_316_mc", "2AMi32o32xxxxxx_tdm8_hibw"),
]


def volume_uncollect(pytestconfig, board, config):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if pytestconfig.getoption("level") == "smoke":
        # Only test master volume on one board at smoke level
        return board != "xk_evk_xu316"
    return False


@pytest.mark.uncollect_if(func=volume_uncollect)
@pytest.mark.parametrize(["board", "config"], volume_configs)
def test_volume_input(pytestconfig, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    num_chans = features["analogue_i"]
    if board == "xk_316_mc" and features["tdm8"]:
        num_chans = 4 # Can only test 4 analogue input channels in tdm without jumper change
    test_chans = ["m", *range(num_chans)]

    duration = 30
    fail_str = ""
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer"),
    ):
        dut.set_stream_format("input", fs, features["chan_i"], 24)

        for channel in test_chans:
            channels = range(num_chans) if channel == "m" else [channel]

            # Load JSON xsig_config data
            xsig_config = f"mc_analogue_input_{num_chans}ch.json"
            xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config
            with open(xsig_config_path) as file:
                xsig_json = json.load(file)

            for ch, ch_config in enumerate(xsig_json["in"]):
                if ch in channels:
                    xsig_json["in"][ch][0] = "volcheck"

            with tempfile.NamedTemporaryFile(mode="w") as xsig_file:
                xsig_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
                json.dump(xsig_json, xsig_file)
                # Need to close file on Windows before xsig can use it
                xsig_file.close()

                with XsigInput(
                    fs,
                    duration,
                    Path(xsig_file.name),
                    dut.dev_name,
                    ident=f"volume_input-{board}-{config}-{channel}",
                ) as xsig_proc:
                    start_time = time.time()
                    # Allow some extra time to ensure xsig has completed
                    end_time = start_time + duration + 7

                    time.sleep(5)

                    dut.volume_reset()
                    time.sleep(3)

                    vol_changes = [0.5, 1.0, 0.75, 1.0]
                    for vol_change in vol_changes:
                        if channel == "m":
                            dut.volume_set_master("input", vol_change)
                        else:
                            dut.volume_set("input", channel, vol_change)
                        time.sleep(3)

                    current_time = time.time()
                    if current_time < end_time:
                        time.sleep(end_time - current_time)

                xsig_lines = xsig_proc.proc_output
                Path(xsig_file.name).unlink()

            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure for channel {channel}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout for channel {channel}\n{xsig_lines}\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=volume_uncollect)
@pytest.mark.parametrize(["board", "config"], volume_configs)
def test_volume_output(pytestconfig, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    num_chans = features["analogue_o"]
    if board == "xk_316_mc" and features["tdm8"]:
        num_chans = 2 # Can only test 2 analogue output channels in tdm without jumper change
    test_chans = ["m", *range(num_chans)]

    xsig_config = f"mc_analogue_output_{num_chans}ch.json"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        for channel in test_chans:
            channels = range(num_chans) if channel == "m" else [channel]

            with (
                AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
                XsigOutput(fs, None, xsig_config_path, dut.dev_name),
            ):
                # Set the channels being tested to 'volume' mode on the analyzer
                analyser_cmds = [f"m {ch} v" for ch in channels]
                ctrl_out, ctrl_err = harness.xscope_controller_cmd(analyser_cmds, cmd_timeout=5)

                dut.volume_reset()
                time.sleep(3)

                vol_changes = [0.5, 1.0, 0.75, 1.0]
                for vol_change in vol_changes:
                    if channel == "m":
                        dut.volume_set_master("output", vol_change)
                    else:
                        dut.volume_set("output", channel, vol_change)
                    time.sleep(3)

                harness.terminate()
                # Some of the volume measurement prints from the analyzer can be captured by the xscope_controller
                # so include all the output from that application as well as the harness output
                xscope_lines = ctrl_out + ctrl_err + harness.proc_stdout + harness.proc_stderr

            # Load JSON xsig config data
            with open(xsig_config_path) as file:
                xsig_json = json.load(file)

            for ch, ch_config in enumerate(xsig_json["out"]):
                if ch in channels:
                    xsig_json["out"][ch][0] = "volcheck"

            failures = check_analyzer_output(xscope_lines, xsig_json["out"])
            if len(failures) > 0:
                fail_str += f"Failure for channel {channel}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xscope stdout for channel {channel}\n{xscope_lines}\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
