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

    with (
        XrunDut(adapter_dut, board, config) as dut,
        AudioAnalyzerHarness(adapter_harness),
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
        pytest.fail(f"{failures}")


@pytest.mark.uncollect_if(func=mixer_uncollect)
@pytest.mark.parametrize(["board", "config"], mixer_configs)
def test_routing_ctrl_output(pytestconfig, ctrl_app, board, config):
    features = get_config_features(board, config)
    fs = max(features["samp_freqs"])
    xsig_config_path = Path(__file__).parent / "xsig_configs" / "mc_analogue_output_8ch.json"
    adapter_dut, adapter_harness = get_xtag_dut_and_harness(pytestconfig, board)
    duration = 10

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
        pytest.fail(f"{failures}")
