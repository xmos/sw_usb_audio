# Copyright 2023-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
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
    ("xk_316_mc", "2AMi32o32xxxxxx_tdm8_mix8_hibw"),
    ("xk_316_mc", "2AMi32o32xxxxxx_tdm8_mix8"),
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

    xsig_config = 'routed_input_8ch'
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config = 'routed_input_4ch'
    xsig_config_path = Path(__file__).parent / "xsig_configs" / f"{xsig_config}.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"]) # To ensure analyser is running before we proceed
        dut.set_stream_format("input", fs, features["chan_i"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        # Route analogue inputs 0, 1, ..., N to host inputs N, N-1, ..., 0 respectively
        num_chans = features["analogue_i"]
        if board == "xk_316_mc" and features["tdm8"]:
            num_chans = 4 # Can only test 4 analogue input channels in tdm without jumper change
        for ch in range(num_chans):
            host_input = features["chan_o"] + num_chans - 1 - ch
            ctrl.set_daw_chan_map(ch, host_input)

        with XsigInput(
            fs,
            duration,
            xsig_config_path,
            dut.dev_name,
            ident=f"routing_ctrl_input-{board}-{config}",
            blocking=True
        ) as xsig_proc:
            pass # do nothing. xsig is running in blocking mode

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
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        # ensure the analyser is running before we proceed.
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
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
    if board == "xk_316_mc" and features["tdm8"]:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"][:2]) # can test only 2 analogue output channels in tdm without jumper change
    else:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += f"xscope stdout at sample rate {fs}\n"
        fail_str += ctrl_out + ctrl_err + xscope_lines + "\n"
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
    if board == "xk_316_mc" and features["tdm8"]:
        xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_4ch.json"
    else:
        xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        AppUsbAudDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"]) # To ensure analyser is running before we proceed
        dut.set_stream_format("input", fs, features["chan_i"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set host inputs (USB IN) from the mixer outputs
        for ch in range(num_chans):
            mixer_offset = features["chan_o"] + features["chan_i"]
            ctrl.set_daw_chan_map(ch, mixer_offset + ch)

        '''
        We want to use USB IN channels as mixer input sources.
        USB IN ch 7 should go out as Mixer output 0
        USB IN ch 6 should go out as Mixer output 1
        ...
        USB IN ch 0 should go out as Mixer output 7

        In the device, the sources are stored as USB OUT channels, USB IN channels, Mixer channels

        mixer_row = features["chan_o"] + (num_mixes - ch - 1), assumes that features["chan_o"] + features["chan_i"]
        is less than or equal to MIX_INPUTS (18), so it can get away with only setting the relevant coefficients in the
        mix_mult_array.
        This is not generally true for tdm8 configs, where there are many more channels.
        In this case, we'll need to set the mix_map instead to map the relevant sources to the mixer inputs.
        '''
        MIX_INPUTS = 18
        if MIX_INPUTS - features["chan_o"] >= num_mixes:
            clear_default_mixes(ctrl, num_mixes)
            # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer, where N is num_mixes
            for ch in range(num_chans):
                mixer_row = features["chan_o"] + (num_mixes - ch - 1)
                ctrl.set_value(0, (mixer_row * num_mixes) + ch, "0")
        else:
            if board == "xk_316_mc" and features["tdm8"]:
                num_chans = 4  # Can only test 4 analogue input channels in tdm without jumper change
            for dst_chan in range(num_chans):
                source_chan = features["chan_o"] + (num_chans -1 - dst_chan)
                ctrl.set_mixer_source(0, dst_chan, source_chan) # first arg 0 implies update for all mixers
            # The default mix should work in this case (pick row 0 for mixer0, row1 for mixer1 and so on)


        with XsigInput(
            fs,
            duration,
            xsig_config_path,
            dut.dev_name,
            ident=f"mixing_ctrl_input-{board}-{config}",
            blocking=True
        ) as xsig_proc:
            pass # do nothing. xsig is running in blocking mode

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
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8

        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["chan_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch)

        clear_default_mixes(ctrl, num_mixes)

        # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer
        for ch in range(num_chans):
            mixer_row = num_chans - ch - 1
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
    if board == "xk_316_mc" and features["tdm8"]:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"][:2]) # can test only 2 analogue output channels in tdm without jumper change
    else:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += f"xscope stdout at sample rate {fs}\n"
        fail_str += ctrl_out + ctrl_err + xscope_lines + "\n"
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
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["chan_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch)

        clear_default_mixes(ctrl, num_mixes)

        # Mix DAW to Analogue (USB OUT) N, N+1 & N+2 in Mixer Output N
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
    if board == "xk_316_mc" and features["tdm8"]:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"][:2]) # can test only 2 analogue output channels in tdm without jumper change
    else:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += f"xscope stdout at sample rate {fs}\n"
        fail_str += ctrl_out + ctrl_err + xscope_lines + "\n"
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
        AudioAnalyzerHarness(adapter_harness, Path(__file__).parents[2] / "sw_audio_analyzer", attach="xscope_app") as harness,
    ):
        ctrl_out, ctrl_err = harness.xscope_controller_cmd([f"x 1"])
        dut.set_stream_format("output", fs, features["chan_o"], 24)

        ctrl = MixerCtrlApp(dut.driver_guid)

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(
                f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})"
            )

        # Set (DEVICE OUT - Analogue [0 ... N]) source to (MIX - Mix [0 ... N])
        mixer_offset = features["chan_o"] + features["chan_i"]
        for ch in range(num_chans):
            ctrl.set_aud_chan_map(ch, mixer_offset + ch) # Mixer outputs routed to device analogue outputs

        # Set mixer(0) input [0 ... N] to device input X (DAW to Analogue (USB OUT) [N ... 0])
        for dst_chan in range(num_chans):
            source_chan = (num_chans -1) - dst_chan
            ctrl.set_mixer_source(0, dst_chan, source_chan) # first arg 0 implies update for all mixers

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.proc_stdout + harness.proc_stderr

    xsig_reversed_chans = (
        Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    )
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    if board == "xk_316_mc" and features["tdm8"]:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"][:2]) # can test only 2 analogue output channels in tdm without jumper change
    else:
        failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += f"xscope stdout at sample rate {fs}\n"
        fail_str += ctrl_out + ctrl_err + xscope_lines + "\n"
        pytest.fail(fail_str)
