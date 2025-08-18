# Copyright 2022-2025 XMOS LIMITED.
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

spdif_smoke_configs = [
    ("xk_216_mc", "2AMi18o18mssaax"),
    ("xk_316_mc", "2AMi10o10xssxxx"),
]


def spdif_common_uncollect(features, board, config, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if features["i2s_loopback"]:
        return True
    if (
        pytestconfig.getoption("level") == "smoke"
        and (board, config) not in spdif_smoke_configs
    ):
        return True
    return False


def spdif_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [
            not features["spdif_i"],
            spdif_common_uncollect(features, board, config, pytestconfig),
        ]
    )


def spdif_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [
            not features["spdif_o"],
            spdif_common_uncollect(features, board, config, pytestconfig),
        ]
    )


def spdif_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration

def get_fs(pytestconfig, features):
    if (pytestconfig.getoption("level") == "smoke") and (platform.system() == "Windows"):
        # On Windows smoke run test only the min and max frequencies
        for f in [min(features["samp_freqs"]), max(features["samp_freqs"])]:
            yield f
    else:
        for f in features["samp_freqs"]:
            yield f

@pytest.mark.order(1)
@pytest.mark.uncollect_if(func=spdif_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_spdif_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        for fs in get_fs(pytestconfig, features):
            assert features["analogue_i"] == 8
            if fs <= 48000:
                num_in_channels = features["analogue_i"] + 2 + (8 * features["adat_i"])
                assert num_in_channels == features["chan_i"]
            elif fs <= 96000:
                num_in_channels = features["analogue_i"] + 2 + (4 * features["adat_i"])
            elif fs <= 192000:
                num_in_channels = features["analogue_i"] + 2 + (2 * features["adat_i"])

            num_dig_in_channels = num_in_channels - features["analogue_i"]
            xsig_config = f'mc_digital_input_analog_{features["analogue_i"]}ch_dig_{num_dig_in_channels}ch'
            if features["adat_i"]:
                xsig_config = (
                    xsig_config + "_spdif"
                )  # If adat is also enabled use a config that only tests spdif
            xsig_config_path = (
                Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
            )

            print(f"spdif_input: config {config}, fs {fs}, num_out_ch {num_in_channels}")

            dut.set_stream_format("input", fs, num_in_channels, 24)

            if features["chan_o"] > num_in_channels:
                dut.set_stream_format("output", fs, num_in_channels, 24)

            with AudioAnalyzerHarness(
                adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", config="spdif_test", attach="xscope_app"
            ) as harness:
                ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"f {fs}"])

                dut.set_clock_src("SPDIF")

                with (
                    XsigInput(
                        fs, duration, xsig_config_path, dut.dev_name, blocking=True
                    ) as xsig_proc,
                ):
                    pass # Nothing to do here. XsigInput is run in blocking mode

                dut.set_clock_src("Internal")

            xsig_lines = xsig_proc.proc_output

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += xsig_lines + "\n\n"
                fail_str += f"Audio analyzer stdout at sample rate {fs}\n"
                # Some of the analyzer output can be captured by the xscope_controller so
                # include all the output from that application as well as the harness output
                analyzer_lines = ctrl_out + ctrl_err + harness.proc_stdout + harness.proc_stderr
                fail_str += analyzer_lines + "\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)


@pytest.mark.order(2)
@pytest.mark.uncollect_if(func=spdif_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_spdif_output(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        for fs in get_fs(pytestconfig, features):
            assert features["analogue_o"] == 8
            num_spdif_out_channels = 2
            if fs <= 48000:
                num_adat_out_channels = 8 * features["adat_o"]
                assert (features["analogue_o"] + num_adat_out_channels + num_spdif_out_channels) == features["chan_o"]
            elif fs <= 96000:
                num_adat_out_channels = 4 * features["adat_o"]
            elif fs <= 192000:
                num_adat_out_channels = 2 * features["adat_o"]

            num_dig_out_channels = num_spdif_out_channels + num_adat_out_channels
            num_out_channels = features["analogue_o"] + num_dig_out_channels
            xsig_config = f'mc_digital_output_analog_{features["analogue_o"]}ch_dig_{num_dig_out_channels}ch'
            if features["adat_o"]:
                xsig_config = (
                    xsig_config + "_spdif"
                )  # When adat is also enabled check only spdif channels
            xsig_config_path = (
                Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
            )

            print(f"spdif_output: config {config}, fs {fs}, num_out_ch {num_out_channels}")

            if features["chan_i"] > num_out_channels:
                dut.set_stream_format("input", fs, num_out_channels, 24)

            dut.set_stream_format("output", fs, num_out_channels, 24)

            with (
                AudioAnalyzerHarness(
                    adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", config="spdif_test", attach="xscope_app"
                ) as harness
            ):
                # Run the analyser using `xrun --xscope-port`, and override the smux command from the host
                # to synchronize startup — this ensures the analyser is running before we proceed.
                ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
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
