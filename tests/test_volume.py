# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import subprocess
import tempfile
import platform

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    get_volcontrol_path,
    get_xscope_controller_path,
    get_tusb_guid,
    stream_format_setup,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import get_config_features


class Volcontrol:
    def __init__(self, input_output, num_chans, channel=None, master=False):
        self.cmd = [get_volcontrol_path()]
        if platform.system() == "Windows":
            self.cmd.append(f"-g{get_tusb_guid()}")
        self.channel = "0" if master else f"{channel + 1}"
        self.reset_chans = f"{num_chans + 1}"
        self.input_output = input_output

    def reset(self):
        cmd = self.cmd + ["--resetall", self.reset_chans]
        subprocess.run(cmd, check=True, timeout=10)
        # sleep after resetting to allow the analyzer to detect the change
        time.sleep(3)

    def set(self, value):
        cmd = self.cmd + ["--set", self.input_output, self.channel, f"{value}"]
        subprocess.run(
            cmd,
            check=True,
            timeout=10,
        )
        # sleep after setting the volume to allow the analyzer to detect the change
        time.sleep(3)


# Test cases are defined by a tuple of (board, config)
volume_configs = [
    ("xk_316_mc", "2AMi10o10xssxxx"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
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
    test_chans = ["m", *range(num_chans)]

    duration = 30
    fail_str = ""
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness),
    ):
        stream_format_setup("input", fs, features["chan_i"], 24)

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

                    if channel == "m":
                        vol_in = Volcontrol("input", num_chans, master=True)
                    else:
                        vol_in = Volcontrol("input", num_chans, channel=int(channel))

                    vol_in.reset()
                    vol_changes = [0.5, 1.0, 0.75, 1.0]
                    for vol_change in vol_changes:
                        vol_in.set(vol_change)

                    current_time = time.time()
                    if current_time < end_time:
                        time.sleep(end_time - current_time)
                    xsig_lines = xsig_proc.get_output()

                Path(xsig_file.name).unlink()

            failures = check_analyzer_output(xsig_lines, xsig_json["in"])
            if len(failures) > 0:
                fail_str += f"Failure for channel {channel}\n"
                fail_str += "\n".join(failures) + "\n\n"
                fail_str += f"xsig stdout for channel {channel}\n"
                fail_str += "\n".join(xsig_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=volume_uncollect)
@pytest.mark.parametrize(["board", "config"], volume_configs)
def test_volume_output(pytestconfig, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    num_chans = features["analogue_o"]
    test_chans = ["m", *range(num_chans)]

    xsig_config = f"mc_analogue_output_{num_chans}ch.json"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    fail_str = ""

    with XrunDut(adapter_dut, board, config) as dut:
        stream_format_setup("output", fs, features["chan_o"], 24)

        for channel in test_chans:
            channels = range(num_chans) if channel == "m" else [channel]

            with (
                AudioAnalyzerHarness(adapter_harness, xscope="app") as harness,
                XsigOutput(fs, None, xsig_config_path, dut.dev_name),
            ):
                # Set the channels being tested to 'volume' mode on the analyzer
                analyser_cmds = [f"m {ch} v" for ch in channels]
                xscope_controller = get_xscope_controller_path()
                ret = subprocess.run(
                    [
                        xscope_controller,
                        "localhost",
                        f"{harness.xscope_port}",
                        "5",  # short timeout to record initial volume value after mode change
                        *analyser_cmds,
                    ],
                    timeout=30,
                    capture_output=True,
                    text=True,
                )
                if ret.returncode != 0:
                    fail_str = (
                        f"xscope_controller command failed, cmds:{analyser_cmds}\n"
                    )
                    fail_str += f"stdout:\n{ret.stdout}\n"
                    fail_str += f"stderr:\n{ret.stderr}\n"
                    pytest.fail(fail_str)

                if channel == "m":
                    vol_out = Volcontrol("output", num_chans, master=True)
                else:
                    vol_out = Volcontrol("output", num_chans, channel=channel)

                vol_out.reset()
                vol_changes = [0.5, 1.0, 0.75, 1.0]
                for vol_change in vol_changes:
                    vol_out.set(vol_change)

                harness.terminate()
                # Some of the volume measurement prints from the analyzer can be captured by the xscope_controller
                # so include all the output from that application as well as the harness output
                xscope_lines = (
                    ret.stdout.splitlines()
                    + ret.stderr.splitlines()
                    + harness.get_output()
                )

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
                fail_str += f"xscope stdout for channel {channel}\n"
                fail_str += "\n".join(xscope_lines) + "\n\n"

    if len(fail_str) > 0:
        pytest.fail(fail_str)
