# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import subprocess
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    get_volcontrol_path,
    get_xscope_controller_path,
    get_tusb_guid,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features


class AdatClockSrc:
    def __init__(self):
        self.cmd = [get_volcontrol_path()]
        if platform.system() == "Windows":
            self.cmd.append(f"-g{get_tusb_guid()}")

    def __enter__(self):
        cmd = self.cmd + ["--clock", "ADAT"]
        subprocess.run(cmd, timeout=10)
        # Short delay to wait for clock source
        time.sleep(5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmd = self.cmd + ["--clock", "Internal"]
        subprocess.run(cmd, timeout=10)


adat_smoke_configs = [
    ("xk_216_mc", "2AMi18o18mssaax"),
    ("xk_316_mc", "2AMi16o16xxxaax"),
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
        duration = 10
    return duration

@pytest.mark.uncollect_if(func=adat_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_adat_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = adat_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            assert features["analogue_i"] == 8

            if fs <= 48000:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 8
                assert(num_in_channels == features["chan_i"])
            elif fs <= 96000:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 4
            else:
                num_in_channels = features["analogue_i"] + (2 * features["spdif_i"]) + 2

            num_dig_in_channels = num_in_channels - features["analogue_i"]

            print(f"adat_input: config {config}, fs {fs}, num_in_ch {num_in_channels}")

            xsig_config = f'mc_digital_input_analog_{features["analogue_i"]}ch_dig_{num_dig_in_channels}ch'
            if(features["spdif_i"]): # If SPDIF is also enabled use the _adat version of the xsig config which checks for ramps only on the ADAT channels
                xsig_config = xsig_config + "_adat"
            xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

            dut.set_stream_format("input", fs, num_in_channels, 24)
            if features["chan_o"] > num_in_channels:
                dut.set_stream_format("output", fs, num_in_channels, 24)
            with AudioAnalyzerHarness(
                adapter_harness, config="adat_test", xscope="app"
            ) as harness:
                xscope_controller = get_xscope_controller_path()
                ret = subprocess.run(
                    [
                        xscope_controller,
                        "localhost",
                        f"{harness.xscope_port}",
                        "0",
                        f"f {fs}",
                    ],
                    timeout=30,
                    capture_output=True,
                    text=True,
                )
                if ret.returncode != 0:
                    fail_str = f'xscope_controller command failed, cmds:["f {fs}"]\n'
                    fail_str += f"stdout:\n{ret.stdout}\n"
                    fail_str += f"stderr:\n{ret.stderr}\n"
                    pytest.fail(fail_str)

                with (
                    AdatClockSrc(),
                ):
                    with(
                        XsigInput(
                        fs, duration, xsig_config_path, dut.dev_name
                    ) as xsig_proc,
                    ):
                        time.sleep(duration + 6)
                        xsig_lines = xsig_proc.get_output()

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)

            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout at sample rate {fs}\n"
                fail_str += "\n".join(xsig_lines) + "\n\n"
                fail_str += f"Audio analyzer stdout at sample rate {fs}\n"
                # Some of the analyzer output can be captured by the xscope_controller so
                # include all the output from that application as well as the harness output
                analyzer_lines = (
                    ret.stdout.splitlines()
                    + ret.stderr.splitlines()
                    + harness.get_output()
                )
                fail_str += "\n".join(analyzer_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)

@pytest.mark.uncollect_if(func=adat_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_adat_output(pytestconfig, board, config):
    features = get_config_features(board, config)

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = adat_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            assert features["analogue_i"] == 8
            if fs <= 48000:
                num_out_channels = features["analogue_o"] + (2 * features["spdif_o"]) + 8
                assert(num_out_channels == features["chan_o"])
                smux = 1
            elif fs <= 96000:
                num_out_channels = features["analogue_o"] + (2 * features["spdif_o"]) + 4
                smux = 2
            else:
                num_out_channels = features["analogue_o"] + (2 * features["spdif_o"]) + 2
                smux = 4

            num_dig_out_channels = num_out_channels - features["analogue_o"]

            print(f"adat_output: config {config}, fs {fs}, num_out_ch {num_out_channels}")

            xsig_config = f'mc_digital_output_analog_{features["analogue_o"]}ch_dig_{num_dig_out_channels}ch'
            if features["spdif_o"]:
                xsig_config = xsig_config + "_adat" # If SPDIF is also enabled use the _adat version of the xsig config which checks for ramps only on the ADAT channels
            xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

            if features["chan_i"] > num_out_channels:
                dut.set_stream_format("input", fs, num_out_channels, 24)
            dut.set_stream_format("output", fs, num_out_channels, 24)

            with AudioAnalyzerHarness(
                adapter_harness, config="adat_test", xscope="app"
            ) as harness:

                xscope_controller = get_xscope_controller_path()
                ret = subprocess.run(
                    [
                        xscope_controller,
                        "localhost",
                        f"{harness.xscope_port}",
                        "0",
                        f"x {smux}",
                    ],
                    timeout=30,
                    capture_output=True,
                    text=True,
                )

                if ret.returncode != 0:
                    fail_str = f'xscope_controller command failed, cmds:["f {fs}"]\n'
                    fail_str += f"stdout:\n{ret.stdout}\n"
                    fail_str += f"stderr:\n{ret.stderr}\n"
                    pytest.fail(fail_str)

                with(XsigOutput(fs, None, xsig_config_path, dut.dev_name)):
                    time.sleep(duration)
                    harness.terminate()
                    xscope_lines = harness.get_output()

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
                fail_str += "\n".join(xscope_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
