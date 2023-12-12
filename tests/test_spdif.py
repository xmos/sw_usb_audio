# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import subprocess
import time
import json
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


class SpdifClockSrc:
    def __init__(self):
        self.cmd = [get_volcontrol_path()]
        if platform.system() == "Windows":
            self.cmd.append(f"-g{get_tusb_guid()}")

    def __enter__(self):
        cmd = self.cmd + ["--clock", "SPDIF"]
        subprocess.run(cmd, timeout=10)
        # Short delay to wait for clock source
        time.sleep(5)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmd = self.cmd + ["--clock", "Internal"]
        subprocess.run(cmd, timeout=10)


def spdif_common_uncollect(features, board, pytestconfig):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if features["i2s_loopback"]:
        return True
    return False


def spdif_input_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["spdif_i"], spdif_common_uncollect(features, board, pytestconfig)]
    )


def spdif_output_uncollect(pytestconfig, board, config):
    features = get_config_features(board, config)
    return any(
        [not features["spdif_o"], spdif_common_uncollect(features, board, pytestconfig)]
    )


def spdif_duration(level, partial):
    if level == "weekend":
        duration = 90 if partial else 1200
    elif level == "nightly":
        duration = 15 if partial else 180
    else:
        duration = 10
    return duration


@pytest.mark.uncollect_if(func=spdif_input_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_spdif_input(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_digital_input_{features["analogue_i"]}ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            with AudioAnalyzerHarness(
                adapter_harness, config="spdif_test", xscope="app"
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
                    SpdifClockSrc(),
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


@pytest.mark.uncollect_if(func=spdif_output_uncollect)
@pytest.mark.parametrize(["board", "config"], list_configs())
def test_spdif_output(pytestconfig, board, config):
    features = get_config_features(board, config)

    xsig_config = f'mc_digital_output_{features["analogue_o"]}ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = spdif_duration(pytestconfig.getoption("level"), features["partial"])
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        for fs in features["samp_freqs"]:
            with (
                AudioAnalyzerHarness(
                    adapter_harness, config="spdif_test", xscope="io"
                ) as harness,
                XsigOutput(fs, None, xsig_config_path, dut.dev_name),
            ):
                time.sleep(duration)
                harness.terminate()
                xscope_lines = harness.get_output()

            with open(xsig_config_path) as file:
                xsig_json = json.load(file)
            failures = check_analyzer_output(xscope_lines, xsig_json["out"])
            if len(failures) > 0:
                fail_str += f"Failure at sample rate {fs}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xscope stdout at sample rate {fs}\n"
                fail_str += "\n".join(xscope_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
