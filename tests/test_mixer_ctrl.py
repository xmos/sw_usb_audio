from pathlib import Path
import pytest
import time
import json
import platform
import subprocess

from hardware_test_tools.check_analyzer_output import check_analyzer_output
from hardware_test_tools.AudioAnalyzerHarness import AudioAnalyzerHarness
from hardware_test_tools.Xsig import XsigInput, XsigOutput
from conftest import list_configs, get_config_features, AppUsbAudDut, get_xtag_dut_and_harness


class MixerCtrlApp:
    def __init__(self, driver_guid):
        bin_name = "xmos_mixer.exe" if platform.system() == "Windows" else "xmos_mixer"
        ctrl_app = Path(__file__).parent / "tools" / bin_name
        if not ctrl_app.exists():
            pytest.fail(f"Mixer control app not found in {ctrl_app}")

        self.ctrl_cmd = [ctrl_app]
        if platform.system() == "Windows" and driver_guid:
            self.ctrl_cmd.append(f"-g{driver_guid}")

    def run_cmd(self, cmd):
        ret = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if ret.returncode != 0:
            fail_str = f"Mixer control app command failed: {cmd}\n" + ret.stdout + ret.stderr
            pytest.fail(fail_str)

    def set_daw_chan_map(self, dst_chan, src_chan):
        cmd = self.ctrl_cmd + ["--set-daw-channel-map", f"{dst_chan}", f"{src_chan}"]
        self.run_cmd(cmd)

    def set_aud_chan_map(self, dst_chan, src_chan):
        cmd = self.ctrl_cmd + ["--set-aud-channel-map", f"{dst_chan}", f"{src_chan}"]
        self.run_cmd(cmd)

    def set_value(self, mixer_id, node, value):
        cmd = self.ctrl_cmd + ["--set-value", f"{mixer_id}", f"{node}", value]
        self.run_cmd(cmd)

    def set_mixer_source(self, mixer_id, dst_chan, src_chan):
        cmd = self.ctrl_cmd + ["--set-mixer-source", f"{mixer_id}", f"{dst_chan}", f"{src_chan}"]
        self.run_cmd(cmd)


mixer_configs = [
    ("xk_216_mc", "2AMi8o10xxsxxx_mix8"),
    ("xk_316_mc", "2AMi8o8xxxxxx_mix8"),
]


def mixer_common_uncollect(pytestconfig, board, config):
    # Check if mixer configs are present for this test level
    if (board, config) not in list_configs():
        return True
    # XTAGs not present
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    if not all(xtag_ids):
        return True
    return False


def mixing_ctrl_output_uncollect(pytestconfig, board, config):
    return mixer_common_uncollect(pytestconfig, board, config)


def mixer_not_smoke_uncollect(pytestconfig, board, config):
    if pytestconfig.getoption("level") == "smoke":
        # Don't run at smoke level
        return True

    return mixer_common_uncollect(pytestconfig, board, config)


@pytest.mark.uncollect_if(func=mixer_not_smoke_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_ctrl_input(pytestconfig, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer"),
    ):
        dut.set_stream_format("input", fs, features["chan_i"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        # Route analogue inputs 0, 1, ..., N to host inputs N, N-1, ..., 0 respectively
        num_chans = features["analogue_i"]
        for ch in range(num_chans):
            host_input = features["chan_o"] + features["analogue_i"] - 1 - ch
            ctrl.set_daw_chan_map(ch, host_input)

        with XsigInput(
            fs,
            duration,
            xsig_config_path,
            dut.dev_name,
            ident=f"routing_ctrl_input-{board}-{config}",
        ) as xsig_proc:
            time.sleep(duration + 6)

        xsig_lines = xsig_proc.proc_output

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xsig_lines, xsig_json["in"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xsig stdout\n" + xsig_lines
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixer_not_smoke_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_ctrl_output(pytestconfig, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    xsig_config_path = (
        Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    )
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope") as harness,
    ):
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        # Route host outputs 0, 1, ..., N to analogue outputs N, N-1, ..., 0 respectively
        num_chans = features["analogue_o"]
        for ch in range(num_chans):
            output_chan = features["analogue_o"] - 1 - ch
            ctrl.set_aud_chan_map(ch, output_chan)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.proc_stdout + harness.proc_stderr

    xsig_routed_config = (
        Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    )
    with open(xsig_routed_config) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n" + xscope_lines
        pytest.fail(fail_str)


def clear_default_mixes(ctrl, num_mixes):
    for ch in range(num_mixes):
        ctrl.set_value(0, (num_mixes * ch) + ch, "-inf")


@pytest.mark.uncollect_if(func=mixer_not_smoke_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_ctrl_input(pytestconfig, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer"),
    ):
        dut.set_stream_format("input", fs, features["chan_i"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set host inputs from the mixer outputs
        for ch in range(num_chans):
            mixer_offset = features["chan_o"] + features["analogue_i"]
            ctrl.set_daw_chan_map(ch, mixer_offset + ch)

        clear_default_mixes(ctrl, num_mixes)

        # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer
        for ch in range(num_chans):
            mixer_row = features["chan_o"] + (num_mixes - ch - 1)
            ctrl.set_value(0, (mixer_row * num_mixes) + ch, "0")

        with XsigInput(
            fs,
            duration,
            xsig_config_path,
            dut.dev_name,
            ident=f"mixing_ctrl_input-{board}-{config}",
        ) as xsig_proc:
            time.sleep(duration + 6)

        xsig_lines = xsig_proc.proc_output

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xsig_lines, xsig_json["in"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xsig stdout\n" + xsig_lines
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixing_ctrl_output_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_ctrl_output(pytestconfig, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = (
        Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    )
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope") as harness,
    ):
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch)

        clear_default_mixes(ctrl, num_mixes)

        # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer
        for ch in range(num_chans):
            mixer_row = num_mixes - ch - 1
            ctrl.set_value(0, (mixer_row * num_mixes) + ch, "0")

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.proc_stdout + harness.proc_stderr

    xsig_reversed_chans = (
        Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    )
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n" + xscope_lines
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixer_not_smoke_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_multi_channel_output(pytestconfig, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = (
        Path(__file__).parent
        / "xsig_configs"
        / "mc_analogue_output_8ch_paired_inverse_sine.json"
    )
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope") as harness,
    ):
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch)

        clear_default_mixes(ctrl, num_mixes)

        # Mix DAW - Analogue N, N+1 & N+2 in Mixer Output N
        for mx in range(num_mixes):
            for i in range(3):
                ctrl.set_value(0, ((mx + i) % num_chans) * num_mixes + mx, "0")

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.proc_stdout + harness.proc_stderr

    xsig_reversed_chans = (
        Path(__file__).parent
        / "xsig_configs"
        / "mc_analogue_output_8ch_paired_inverse_sine_result.json"
    )
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n" + xscope_lines
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixer_not_smoke_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_daw_out_mix_input(pytestconfig, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = (
        Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    )
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope") as harness,
    ):
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set (DEVICE OUT - Analogue [0 ... N]) source to (MIX - Mix [0 ... N])
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch)

        # Set mixer(0) input [0 ... N] to device input X (DAW - Analogue [N ... 0])
        for mx in range(num_mixes):
            ctrl.set_mixer_source(0, mx, (num_chans -1) - mx)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.proc_stdout + harness.proc_stderr

    xsig_reversed_chans = (
        Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    )
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n" + xscope_lines
        pytest.fail(fail_str)
