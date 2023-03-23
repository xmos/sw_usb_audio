from pathlib import Path
import pytest
import time
import json
import platform
import subprocess

from usb_audio_test_utils import (
    check_analyzer_output,
    get_xtag_dut_and_harness,
    AudioAnalyzerHarness,
    XrunDut,
    XsigInput,
    XsigOutput,
)
from conftest import list_configs, get_config_features


@pytest.fixture(scope="module")
def ctrl_app():
    bin_name = "xmos_mixer.exe" if platform.system() == "Windows" else "xmos_mixer"
    ctrl_app = Path(__file__).parent / "tools" / bin_name
    if not ctrl_app.exists():
        pytest.fail(f"Mixer control app not found in {ctrl_app}")
    return ctrl_app


mixer_configs = [
    ("xk_216_mc", "2AMi8o10xxsxxx_mix8"),
    ("xk_316_mc", "2AMi8o8xxxxxx_mix8"),
]


def mixer_uncollect(pytestconfig, board, config):
    # Check if mixer configs are present for this test level
    if (board, config) not in list_configs():
        return True
    # XTAGs not present
    xtag_ids = get_xtag_dut_and_harness(pytestconfig, board)
    if not all(xtag_ids):
        return True
    return False


@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_ctrl_input(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness) as harness,
    ):

        # Route analogue inputs 0, 1, ..., N to host inputs N, N-1, ..., 0 respectively
        num_chans = features["analogue_i"]
        for ch in range(num_chans):
            host_input = features["chan_o"] + features["analogue_i"] - 1 - ch
            mixer_cmd = [ctrl_app, "--set-daw-channel-map", f"{ch}", f"{host_input}"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigInput(fs, duration, xsig_config_path, dut.dev_name) as xsig_proc:
            time.sleep(duration + 6)
            xsig_lines = xsig_proc.get_output()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xsig_lines, xsig_json["in"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xsig stdout\n"
        fail_str += "\n".join(xsig_lines)
        harness_output = harness.get_output()
        if len(harness_output) > 0:
            fail_str += "\n\nAudio analyzer stdout\n"
            fail_str += "\n".join(harness_output)
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_ctrl_output(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
    ):

        # Route host outputs 0, 1, ..., N to analogue outputs N, N-1, ..., 0 respectively
        num_chans = features["analogue_o"]
        for ch in range(num_chans):
            output_chan = features["analogue_o"] - 1 - ch
            mixer_cmd = [ctrl_app, "--set-aud-channel-map", f"{ch}", f"{output_chan}"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.get_output()

    xsig_routed_config = Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    with open(xsig_routed_config) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n"
        fail_str += "\n".join(xscope_lines)
        pytest.fail(fail_str)


def clear_default_mixes(ctrl_app, num_mixes):
    for ch in range(num_mixes):
        mixer_cmd = [ctrl_app, "--set-value", "0", f"{(num_mixes * ch) + ch}", "-inf"]
        subprocess.run(mixer_cmd, timeout=10)


@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_ctrl_input(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "routed_input_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness) as harness,
    ):

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})")

        # Set host inputs from the mixer outputs
        for ch in range(num_chans):
            mixer_offset = features["chan_o"] + features["analogue_i"]
            mixer_cmd = [ctrl_app, "--set-daw-channel-map", f"{ch}", f"{mixer_offset + ch}"]
            subprocess.run(mixer_cmd, timeout=10)

        clear_default_mixes(ctrl_app, num_mixes)

        # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer
        for ch in range(num_chans):
            mixer_row = features["chan_o"] + (num_mixes - ch - 1)
            mixer_cmd = [ctrl_app, "--set-value", "0", f"{(mixer_row * num_mixes) + ch}", "0"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigInput(fs, duration, xsig_config_path, dut.dev_name) as xsig_proc:
            time.sleep(duration + 6)
            xsig_lines = xsig_proc.get_output()

    with open(xsig_config_path) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xsig_lines, xsig_json["in"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xsig stdout\n"
        fail_str += "\n".join(xsig_lines)
        harness_output = harness.get_output()
        if len(harness_output) > 0:
            fail_str += "\n\nAudio analyzer stdout\n"
            fail_str += "\n".join(harness_output)
        pytest.fail(fail_str)


@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_ctrl_output(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
    ):

        num_mixes = 8
        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})")

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            mixer_cmd = [ctrl_app, "--set-aud-channel-map", f"{ch}", f"{mixer_offset + ch}"]
            subprocess.run(mixer_cmd, timeout=10)

        clear_default_mixes(ctrl_app, num_mixes)

        # Reverse the channels 0, 1, ..., N to N, N-1, ..., 0 inside the mixer
        for ch in range(num_chans):
            mixer_row = num_mixes - ch - 1
            mixer_cmd = [ctrl_app, "--set-value", "0", f"{(mixer_row * num_mixes) + ch}", "0"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.get_output()

    xsig_reversed_chans = Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n"
        fail_str += "\n".join(xscope_lines)
        pytest.fail(fail_str)

@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_mixing_multi_channel_output(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch_paired_inverse_sine.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
    ):

        num_mixes = 8
        num_chans = features["analogue_o"]
        if num_chans > num_mixes:
            pytest.fail(f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})")

        # Set analogue outputs from the mixer outputs
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            mixer_cmd = [ctrl_app, "--set-aud-channel-map", f"{ch}", f"{mixer_offset + ch}"]
            subprocess.run(mixer_cmd, timeout=10)

        clear_default_mixes(ctrl_app, num_mixes)

        # Mix DAW - Analogue N, N+1 & N+2 in Mixer Output N
        for mx in range(num_mixes):
            mixer_cmd = [ctrl_app, "--set-value", "0", f"{((mx + 0) % num_chans) * num_mixes + mx}", "0"]
            subprocess.run(mixer_cmd, timeout=10)
            mixer_cmd = [ctrl_app, "--set-value", "0", f"{((mx + 1) % num_chans) * num_mixes + mx}", "0"]
            subprocess.run(mixer_cmd, timeout=10) 
            mixer_cmd = [ctrl_app, "--set-value", "0", f"{((mx + 2) % num_chans) * num_mixes + mx}", "0"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.get_output()

    xsig_reversed_chans = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch_paired_inverse_sine_result.json"
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n"
        fail_str += "\n".join(xscope_lines)
        pytest.fail(fail_str)

@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_daw_out_mix_input(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    # Limit to 96kHz to be able to use all 8 mixes
    fs = min(96000, max([f for f in features["samp_freqs"] if f <= 96000]))
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10
    fail_str = ""

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness, xscope="io") as harness,
    ):

        num_mixes = 8
        num_chans = features["analogue_i"]
        if num_chans > num_mixes:
            pytest.fail(f"Unsupported number of channels ({num_chans}) and mixes ({num_mixes})")

        # Set (DEVICE OUT - Analogue [0 ... N]) source to (MIX - Mix [0 ... N])
        mixer_offset = features["chan_o"] + features["analogue_i"]
        for ch in range(num_chans):
            mixer_cmd = [ctrl_app, "--set-aud-channel-map", f"{ch}", f"{mixer_offset + ch}"]
            subprocess.run(mixer_cmd, timeout=10)

        # Set mixer(0) input [0 ... N] to device input X (DAW - Analogue [N ... 0])
        for mx in range(num_mixes):
            mixer_cmd = [ctrl_app, "--set-mixer-source", "0", f"{mx}", f"{(num_chans -1) - mx}"]
            subprocess.run(mixer_cmd, timeout=10)

        with XsigOutput(fs, None, xsig_config_path, dut.dev_name):
            time.sleep(duration)
            harness.terminate()
            xscope_lines = harness.get_output()

    xsig_reversed_chans = Path(__file__).parent / "xsig_configs" / "routed_output_8ch.json"
    with open(xsig_reversed_chans) as file:
        xsig_json = json.load(file)
    failures = check_analyzer_output(xscope_lines, xsig_json["out"])
    if len(failures) > 0:
        fail_str += "\n".join(failures) + "\n\n"
        fail_str += "xscope stdout\n"
        fail_str += "\n".join(xscope_lines)
        pytest.fail(fail_str)
