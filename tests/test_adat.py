# Copyright 2022-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
from pathlib import Path
import pytest
import time
import json

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.AudioAnalyzerHarness import AudioAnalyzerHarness
from hardware_test_tools.Xsig import XsigInput, XsigOutput
from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut_and_harness

adat_smoke_configs = [
    ("xk_216_mc", "2AMi18o18mssaax"),
    ("xk_316_mc", "2AMi16o16xxxaax"),
    ("xk_316_mc", "2AMi30o30xxxaax_hibw"),
    ("xk_316_mc", "2AMi20o20xxxaax_hibw"),
]

def adat_common_uncollect(features, board, config, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if features["i2s_loopback"]:
        return True
    if (
        pytestconfig.getoption("level") == "smoke"
        and (board, config) not in adat_smoke_configs
    ):
        return True
    return False


def adat_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["adat_i"], adat_common_uncollect(features, board, config, pytestconfig)]
    )


def adat_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["adat_o"], adat_common_uncollect(features, board, config, pytestconfig)]
    )


def adat_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 5
    return duration

def set_clock(dut, clk_src):
    assert clk_src in ["Internal", "ADAT"], f"Invalid clock source {clk_src}, must be Internal or ADAT"
    clk_src_retry_count = 0
    num_clk_src_retries = 2
    while clk_src_retry_count < num_clk_src_retries:
        ret = dut.set_clock_src(clk_src)
        if ret == 0:
            break
        clk_src_retry_count += 1
        time.sleep(4)
    assert clk_src_retry_count < num_clk_src_retries, f"Failed to set clock source to {clk_src} after {num_clk_src_retries} retries"

@pytest.mark.uncollect_if(func=adat_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_adat_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = adat_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    print("samp_freqs = ", features["samp_freqs"])

    # Swapped the order of the for and the with to workaround weird MacOS issue where it seems to hang after changing the clock source between ADAT and Internal after about 4 iterations.
    # Restarting the DUT after each fs iteration seems to fix the issue.
    for fs in features["samp_freqs"]:
        with AppUsbAudDut(adapter_dut, board, config) as dut:
            assert features["analogue_i"] == 8
            if fs <= 48000:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 8
                smux = 1
            elif fs <= 96000:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 4
                smux = 2
            else:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 2
                smux = 4

            if features["hibw"]:
                # This must be a HiBW config. Keep num_in_channels, same as NUM_USB_CHAN_IN (so 30 for i30o30 config)
                num_in_channels = features["chan_i"]
                if smux == 1:
                    num_dig_in_channels = 8
                elif smux == 2:
                    num_dig_in_channels = 4
                else:
                    num_dig_in_channels = 2
                dont_care_channels = num_in_channels - features["analogue_i"] - (2 * features["spdif_i"]) - num_dig_in_channels
                xsig_config = f'mc_digital_input_analog_{features["analogue_i"]}ch_dig_{num_dig_in_channels}ch_dont_care_{dont_care_channels}ch'
                # Choose always the format with all the channels (instead of channels - 4 or channels -6) since with HiBW enabled, there's enough BW to support the highest sample rate at features["chan_i"]
                dut._set_full_stream_format(fs, num_in_channels, 24, num_in_channels, 24, True) # call low-level function to bypass the 10 channel limit check for 176.4, 192kHz
            else:
                num_dig_in_channels = num_in_channels - features["analogue_i"]
                xsig_config = f'mc_digital_input_analog_{features["analogue_i"]}ch_dig_{num_dig_in_channels}ch'
                if(features["spdif_i"]): # If SPDIF is also enabled use the _adat version of the xsig config which checks for ramps only on the ADAT channels
                    xsig_config = xsig_config + "_adat"
                dut.set_stream_format("input", fs, num_in_channels, 24)
                if features["chan_o"] > num_in_channels:
                    dut.set_stream_format("output", fs, num_in_channels, 24)

            print(f"adat_input: config {config}, fs {fs}, num_in_ch {num_in_channels}, smux = {smux}")

            xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"


            with AudioAnalyzerHarness(
                adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", config="adat_test", attach="xscope_app"
            ) as harness:
                ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"f {fs}"])

                set_clock(dut, "ADAT")

                with (
                    XsigInput(
                        fs, duration, xsig_config_path, dut.dev_name, blocking=True
                    ) as xsig_proc,
                ):
                    pass # Nothing to do here. XsigInput is run in blocking mode

                set_clock(dut, "Internal")

            xsig_lines = xsig_proc.proc_output

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)

            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += xsig_lines + "\n"
                fail_str += f"Audio analyzer stdout at sample rate {fs}\n"
                # Some of the analyzer output can be captured by the xscope_controller so
                # include all the output from that application as well as the harness output
                analyzer_lines = ctrl_out + ctrl_err + harness.proc_stdout + harness.proc_stderr
                fail_str += analyzer_lines + "\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)

@pytest.mark.uncollect_if(func=adat_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_adat_output(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = adat_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with AppUsbAudDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            assert features["analogue_i"] == 8
            if fs <= 48000:
                num_adat_out_channels = 8
                smux = 1
            elif fs <= 96000:
                num_adat_out_channels = 4
                smux = 2
            else:
                num_adat_out_channels = 2
                smux = 4

            if features["hibw"]:
                # This must be a HiBW config. Keep num_out_channels, same as NUM_USB_CHAN_OUT (so 30 for i30o30 config)
                num_out_channels = features["chan_o"]
                dont_care_channels = num_out_channels - features["analogue_o"] - (2 * features["spdif_o"]) - num_adat_out_channels
                xsig_config = f'mc_digital_output_analog_{features["analogue_o"]}ch_dig_{num_adat_out_channels}ch_dont_care_{dont_care_channels}ch'
                # Choose always the format with all the channels (instead of (channels - 4) or (channels - 6)) since with HiBW enabled, there's enough BW to support the highest sample rate at features["chan_i"]
                dut._set_full_stream_format(fs, num_out_channels, 24, num_out_channels, 24, True) # call low-level function to bypass the 10 channel limit check for 176.4, 192kHz
            else:
                num_dig_out_channels = (2 * features["spdif_o"]) + num_adat_out_channels
                num_out_channels = features["analogue_o"] + num_dig_out_channels
                dont_care_channels = 0
                xsig_config = f'mc_digital_output_analog_{features["analogue_o"]}ch_dig_{num_dig_out_channels}ch'
                if features["chan_i"] > num_out_channels:
                    dut.set_stream_format("input", fs, num_out_channels, 24)
                dut.set_stream_format("output", fs, num_out_channels, 24)

            print(f"adat_output: config {config}, fs {fs}, num_out_ch {num_out_channels}, smux = {smux}")

            if features["spdif_o"]:
                xsig_config = xsig_config + "_adat" # If SPDIF is also enabled use the _adat version of the xsig config which checks for ramps only on the ADAT channels
            xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"


            with AudioAnalyzerHarness(
                adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", config="adat_test", attach="xscope_app"
            ) as harness:
                ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x {smux}"])

                with(XsigOutput(fs, 0, xsig_config_path, dut.dev_name) as xsig_proc):
                    time.sleep(duration)
                    harness.terminate()
                    xscope_lines = harness.proc_stdout + harness.proc_stderr

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
                if features["spdif_o"]: # If spdif is also enabled, rearrange xsig_json so adat output is expected channel 8 onwards since that's how the analyser prints it
                    for i in range(8, num_out_channels-2):
                        xsig_json['out'][i] = xsig_json['out'][i+2]
                    for i in range(num_out_channels-2, num_out_channels):
                        xsig_json['out'][i] = ["zero"]
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
