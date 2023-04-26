import pytest
import subprocess
from pathlib import Path
import platform
import re
import shutil


def pytest_addoption(parser):
    parser.addoption(
        "--level",
        action="store",
        default="smoke",
        choices=["smoke", "nightly", "weekend"],
        help="Test coverage level",
    )

    parser.addini("xk_216_mc_dut", help="XTAG ID for xk_216_mc DUT")
    parser.addini("xk_216_mc_harness", help="XTAG ID for xk_216_mc harness")
    parser.addini("xk_316_mc_dut", help="XTAG ID for xk_316_mc DUT")
    parser.addini("xk_316_mc_harness", help="XTAG ID for xk_316_mc harness")
    parser.addini("xk_evk_xu316_dut", help="XTAG ID for xk_evk_xu316 DUT")
    parser.addini("xk_evk_xu316_harness", help="XTAG ID for xk_evk_xu316 harness")


boards = ["xk_216_mc", "xk_316_mc", "xk_evk_xu316"]


board_configs = {}


all_freqs = [44100, 48000, 88200, 96000, 176400, 192000]

def samp_freqs_upto(max):
    return [fs for fs in all_freqs if fs <= max]


def parse_features(board, config):
    max_analogue_chans = 8

    config_re = r"^(?P<uac>[12])(?P<sync_mode>[ADS])(?P<i2s>[MSX])i(?P<chan_i>\d+)o(?P<chan_o>\d+)(?P<midi>[mx])(?P<spdif_i>[sx])(?P<spdif_o>[sx])(?P<adat_i>[ax])(?P<adat_o>[ax])(?P<dsd>[dx])(?P<tdm8>(_tdm8)?)"
    match = re.search(config_re, config)
    if not match:
        pytest.exit(f"Error: Unable to parse features from {config}")

    # Form dictionary of features then convert items to integers or boolean as required
    features = match.groupdict()
    for k in ["uac", "chan_i", "chan_o"]:
        features[k] = int(features[k])
    for k in ["midi", "spdif_i", "spdif_o", "adat_i", "adat_o", "dsd", "tdm8"]:
        features[k] = features[k] not in ["", "x"]

    if not features["uac"] in [1, 2]:
        pytest.exit(f"Error: Invalid UAC in {config}")

    if board == "xk_216_mc":
        if config.startswith("1"):
            features["pid"] = 0xF
        else:
            features["pid"] = 0xE
    elif board == "xk_316_mc":
        if config.startswith("1"):
            features["pid"] = 0x17
        else:
            features["pid"] = 0x16 if not "_winbuiltin" in config else 0x1a
    elif board == "xk_evk_xu316":
        if config.startswith("1"):
            features["pid"] = 0x19
        else:
            features["pid"] = 0x18

    # Set the number of analogue channels
    features["analogue_i"] = min(features["chan_i"], max_analogue_chans)
    features["analogue_o"] = min(features["chan_o"], max_analogue_chans)
    if "noi2s" in config:
        # Force analogue channels to zero
        features["analogue_i"] = 0
        features["analogue_o"] = 0
    elif "i2sloop" in config:
        # The analogue output channels are looped back to the inputs preventing their use
        features["analogue_i"] = 0

    # Create list of supported sample frequencies
    if config == "1AMi8o2xxxxxx":
        features["samp_freqs"] = samp_freqs_upto(44100)
    elif features["uac"] == 1:
        if features["chan_i"] and features["chan_o"]:
            features["samp_freqs"] = samp_freqs_upto(48000)
        else:
            features["samp_freqs"] = samp_freqs_upto(96000)
    elif features["chan_i"] >= 32 or features["chan_o"] >= 32:
        features["samp_freqs"] = samp_freqs_upto(48000)
    elif features["chan_i"] >= 16 or features["chan_o"] >= 16:
        features["samp_freqs"] = samp_freqs_upto(96000)
    elif features["tdm8"]:
        features["samp_freqs"] = samp_freqs_upto(96000)
    else:
        features["samp_freqs"] = samp_freqs_upto(192000)

    return features


def pytest_sessionstart(session):
    usb_audio_dir = Path(__file__).parents[1]
    app_prefix = "app_usb_aud_"
    exclude_app = ["app_usb_aud_xk_evk_xu316_extrai2s"]

    test_level = session.config.getoption("level")

    for app_dir in usb_audio_dir.iterdir():
        app_name = app_dir.name
        if not app_name.startswith(app_prefix) or app_name in exclude_app:
            continue

        board = app_name[len(app_prefix) :]

        # Get all the configs, and determine which will be fully- or partially-tested
        allconfigs_cmd = ["xmake", "allconfigs"]
        ret = subprocess.run(
            allconfigs_cmd, capture_output=True, text=True, cwd=app_dir
        )
        full_configs = ret.stdout.split()

        if test_level in ["nightly", "weekend"]:
            allconfigs_cmd.append("PARTIAL_TEST_CONFIGS=1")
            ret = subprocess.run(
                allconfigs_cmd, capture_output=True, text=True, cwd=app_dir
            )
            configs = ret.stdout.split()
        else:
            configs = full_configs

        # On Windows also collect special configs that will use the built-in driver
        if platform.system() == "Windows":
            winconfigs_cmd = ["xmake", "TEST_SUPPORT_CONFIGS=1", "allconfigs"]
            ret = subprocess.run(
                winconfigs_cmd, capture_output=True, text=True, cwd=app_dir
            )
            configs += [cfg for cfg in ret.stdout.split() if "_winbuiltin" in cfg]

        partial_configs = [config for config in configs if config not in full_configs]
        for config in configs:
            global board_configs
            features = parse_features(board, config)
            # Mark the relevant configs for partial testing only
            features["partial"] = config in partial_configs
            board_configs[f"{board}-{config}"] = features


def list_configs():
    return [tuple(k.split("-", maxsplit=1)) for k in board_configs.keys()]


def get_config_features(board, config):
    return board_configs[f"{board}-{config}"]


# Dictionary indexed by board name, with each entry being the tuple of XTAG IDs for
# the DUT and harness for that board, (None, None) if XTAGs for board not provided.
xtag_dut_harness = {}


def pytest_configure(config):
    global xtag_dut_harness

    # Populate the global xtag_dut_harness dictionary with the XTAG IDs that were set
    # in pytest.ini or overridden on the command-line
    for board in boards:
        dut = config.getini(f"{board}_dut")
        harness = config.getini(f"{board}_harness")
        xtag_dut_harness[board] = (dut, harness)


def pytest_collection_modifyitems(config, items):
    selected = []
    deselected = []

    # Deselect testcases which use hardware that doesn't have an XTAG ID
    for item in items:
        m = item.get_closest_marker("uncollect_if")
        if m:
            func = m.kwargs["func"]
            if func(config, **item.callspec.params):
                deselected.append(item)
            else:
                selected.append(item)

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected


# Print a session-level warning if usbdeview is not available on Windows
def pytest_terminal_summary(terminalreporter):
    if platform.system() == "Windows" and not shutil.which("usbdeview"):
        terminalreporter.section("Session warning")
        terminalreporter.write(
            "usbdeview not on PATH so test device data has not been cleared"
        )
