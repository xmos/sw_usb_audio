# Copyright (c) 2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import time
import json
import subprocess
import tempfile

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import get_config_features


class Volcontrol:
    EXECUTABLE = Path(__file__).parent / "tools" / "volcontrol" / "volcontrol"

    def __init__(self, input_output, num_chans, channel=None, master=False):
        self.channel = "0" if master else f"{channel + 1}"
        self.reset_chans = f"{num_chans + 1}"
        self.input_output = input_output

    def reset(self):
        subprocess.run([self.EXECUTABLE, "--resetall", self.reset_chans], check=True, timeout=10)
        # sleep after resetting to allow the analyzer to detect the change
        time.sleep(3)

    def set(self, value):
        subprocess.run(
            [self.EXECUTABLE, "--set", self.input_output, self.channel, f"{value}"],
            check=True,
            timeout=10,
        )
        # sleep after setting the volume to allow the analyzer to detect the change
        time.sleep(3)


# Test cases are defined by a tuple of (board, config, sample rate, 'm' (master) or channel number)
volume_configs = [
    *[("xk_316_mc", "2AMi10o10xssxxx", 96000, ch) for ch in ["m", *range(8)]],
    *[("xk_evk_xu316", "2AMi2o2xxxxxx", 48000, ch) for ch in ["m", *range(2)]],
]


def volume_uncollect(pytestconfig, board, config, fs, channel):
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    # XTAGs not present
    if not all(xtag_ids):
        return True
    if pytestconfig.getoption("level") == "smoke":
        # Only test master volume on one board at smoke level
        return board != "xk_316_mc" or channel != "m"
    return False


@pytest.mark.uncollect_if(func=volume_uncollect)
@pytest.mark.parametrize(["board", "config", "fs", "channel"], volume_configs)
def test_volume_input(pytestconfig, board, config, fs, channel):
    features = get_config_features(board, config)
    num_chans = features["analogue_i"]
    channels = range(num_chans) if channel == "m" else [channel]

    duration = 25

    # Load JSON xsig_config data
    xsig_config = f"mc_analogue_input_{num_chans}ch.json"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    for ch, ch_config in enumerate(xsig_json["in"]):
        if ch in channels:
            xsig_json["in"][ch][0] = "volcheck"

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness) as harness,
        tempfile.NamedTemporaryFile(mode="w") as xsig_file,
    ):

        json.dump(xsig_json, xsig_file)
        xsig_file.flush()

        with XsigInput(fs, duration, Path(xsig_file.name), dut.dev_name) as xsig_proc:
            start_time = time.time()
            # Allow five extra seconds to ensure xsig has completed
            end_time = start_time + duration + 5

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

    # Check output
    check_analyzer_output(xsig_lines, xsig_json["in"])


@pytest.mark.uncollect_if(func=volume_uncollect)
@pytest.mark.parametrize(["board", "config", "fs", "channel"], volume_configs)
def test_volume_output(pytestconfig, board, config, fs, channel):
    features = get_config_features(board, config)
    num_chans = features["analogue_o"]
    channels = range(num_chans) if channel == "m" else [channel]

    xsig_config = f"mc_analogue_output_{num_chans}ch.json"
    xsig_config_path = Path(__file__).parent / "xsig_configs" / xsig_config

    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="app") as harness,
        XsigOutput(fs, None, xsig_config_path, dut.dev_name),
    ):

        # Set the channels being tested to 'volume' mode on the analyzer
        analyser_cmds = [f"m {ch} v" for ch in channels]
        xscope_controller = (
            Path(__file__).parents[2]
            / "sw_audio_analyzer"
            / "host_xscope_controller"
            / "bin_macos"
            / "xscope_controller"
        )
        subprocess.run(
            [
                xscope_controller,
                "localhost",
                f"{harness.xscope_port}",
                "0",
                *analyser_cmds,
            ],
            check=True,
            timeout=10,
        )

        time.sleep(2)

        if channel == "m":
            vol_out = Volcontrol("output", num_chans, master=True)
        else:
            vol_out = Volcontrol("output", num_chans, channel=channel)

        vol_out.reset()
        vol_changes = [0.5, 1.0, 0.75, 1.0]
        for vol_change in vol_changes:
            vol_out.set(vol_change)

        harness.terminate()
        xscope_lines = harness.get_output()

    # Load JSON xsig config data
    with open(xsig_config_path) as file:
        xsig_json = json.load(file)

    for ch, ch_config in enumerate(xsig_json["out"]):
        if ch in channels:
            xsig_json["out"][ch][0] = "volcheck"

    check_analyzer_output(xscope_lines, xsig_json["out"])
