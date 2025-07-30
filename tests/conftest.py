# Copyright 2020-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
import pytest
from pathlib import Path
import platform
import re
import shutil
import yaml

from hardware_test_tools.UaDut import UaDut
from hardware_test_tools.pnputil_remove_device import remove_xmos_device_nodes


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

    config_re = r"^(?P<uac>[12])(?P<sync_mode>[ADS])(?P<i2s>[MSX])i(?P<chan_i>\d+)o(?P<chan_o>\d+)(?P<midi>[mx])(?P<spdif_i>[sx])(?P<spdif_o>[sx])(?P<adat_i>[ax])(?P<adat_o>[ax])(?P<dsd>[dx])(?P<tdm8>(_tdm8)?)(?P<hibw>(_hibw)?)"
    match = re.search(config_re, config)
    if not match:
        pytest.exit(f"Error: Unable to parse features from {config}")

    # Form dictionary of features then convert items to integers or boolean as required
    features = match.groupdict()
    for k in ["uac", "chan_i", "chan_o"]:
        features[k] = int(features[k])
    for k in ["midi", "spdif_i", "spdif_o", "adat_i", "adat_o", "dsd", "tdm8", "hibw"]:
        features[k] = features[k] not in ["", "x"]

    if features["uac"] not in [1, 2]:
        pytest.exit(f"Error: Invalid UAC in {config}")

    if board == "xk_216_mc":
        if config.startswith("1"):
            features["pid"] = (0xF, 0xD00F) # Runtime mode and DFU mode PIDs
        else:
            features["pid"] = (0xE, 0xD00E)
    elif board == "xk_316_mc":
        if config.startswith("1"):
            features["pid"] = (0x17, 0xD017)
        else:
            features["pid"] = (0x16, 0xD016) if "_winbuiltin" not in config else (0x1A, 0xD01A)
    elif board == "xk_evk_xu316":
        if config.startswith("1"):
            features["pid"] = (0x19, 0xD019)
        else:
            features["pid"] = (0x18, 0xD018)

    # Set the number of analogue channels
    features["analogue_i"] = min(features["chan_i"], max_analogue_chans)
    features["analogue_o"] = min(features["chan_o"], max_analogue_chans)
    if "noi2s" in config:
        # Force analogue channels to zero
        features["analogue_i"] = 0
        features["analogue_o"] = 0

    # Handle HiBW configs
    if(features["hibw"]):
        # This must be a HiBW config. Figure out the max samp freq it can support
        max_txns_per_microframe = 2
        max_txn_length = 1024
        max_transfer_length = max_txns_per_microframe * max_txn_length
        if((192000/8000) * features["chan_i"] * 4 < max_transfer_length):
            features["samp_freqs"] = samp_freqs_upto(192000)
        elif ((96000/8000) * features["chan_i"] * 4 < max_transfer_length):
            features["samp_freqs"] = samp_freqs_upto(96000)
        elif ((48000/8000) * features["chan_i"] * 4 < max_transfer_length):
            features["samp_freqs"] = samp_freqs_upto(48000)
        else:
            assert False, f"{features['chan_i']} cannot be supported by the HiBW implementation supporting a max transfer size of {max_transfer_length}"
        #print(f"HiBW config {config} with {features['chan_i']} input channels, supporting sample frequencies {features['samp_freqs']}")
    else:
        features["hibw"] = False
        if config == "1AMi8o2xxxxxx":
            features["samp_freqs"] = samp_freqs_upto(44100)
        elif features["uac"] == 1:
            if features["chan_i"] and features["chan_o"]:
                features["samp_freqs"] = samp_freqs_upto(48000)
            else:
                features["samp_freqs"] = samp_freqs_upto(96000)
        elif features["chan_i"] >= 32 or features["chan_o"] >= 32:
            features["samp_freqs"] = samp_freqs_upto(48000)
        elif (not features["adat_i"] and features["chan_i"] >= 16) or (
            not features["adat_o"] and features["chan_o"] >= 16
        ):
            features["samp_freqs"] = samp_freqs_upto(96000)
        elif (features["adat_i"] and features["chan_i"] > 16) or (features["adat_o"] and features["chan_i"] > 16): #i18o18 build
            features["samp_freqs"] = samp_freqs_upto(96000)
        elif features["tdm8"]:
            features["samp_freqs"] = samp_freqs_upto(96000)
        else:
            features["samp_freqs"] = samp_freqs_upto(192000)

    features["i2s_loopback"] = False
    return features

def pytest_sessionstart(session):
    if platform.system() == "Windows":
        print("Deleting any existing device nodes before running tests...")
        remove_xmos_device_nodes(0x20b1) # remove any existing nodes of previously disconnected devices before running tests

    usb_audio_dir = Path(__file__).parents[1]
    app_prefix = "app_usb_aud_"
    exclude_app = ["app_usb_aud_xk_evk_xu316_extrai2s"]

    with open(Path(__file__).parent / "app_configs_autogen.yml") as fp:
        try:
            config_dict = yaml.safe_load(fp)
        except yaml.YAMLError as exc:
            print(exc)
            assert False

    for app_dir in usb_audio_dir.iterdir():
        app_name = app_dir.name
        if not app_name.startswith(app_prefix) or (app_name in exclude_app) or ("@" in app_name):
            continue

        board = app_name[len(app_prefix) :]
        assert app_name in config_dict

        full_configs = config_dict[app_name]['full_configs']
        partial_configs = config_dict[app_name]['partial_configs']
        all_configs = [*full_configs, *partial_configs]

        for config in all_configs:
            global board_configs
            features = parse_features(board, config)
            # Mark the relevant configs for partial testing only
            features["partial"] = config in partial_configs
            board_configs[f"{board}-{config}"] = features

            # add in the i2s loopback configs used for testing on 316
            if board == "xk_316_mc":
                features_i2sloopback = features.copy()
                features_i2sloopback["i2s_loopback"] = True
                features_i2sloopback["analogue_i"] = 0
                board_configs[f"{board}-{config}_i2sloopback"] = features_i2sloopback


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
        else: # If test doesn't define an uncollect function, default behaviour is to collect it
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


def get_firmware_path(board, config):
    # XE can be called app_usb_aud_{board}.xe or app_usb_aud_{board}_{config}.xe
    xe_name = f"app_usb_aud_{board}_{config}.xe"
    if config:
        fw_path_base = Path(__file__).parents[1] / f"app_usb_aud_{board}" / "bin" / config
        fw_path = fw_path_base / xe_name
    else:
        xe_name = f"app_usb_aud_{board}.xe"
        fw_path = fw_path_base / xe_name
    if not fw_path.exists():
        pytest.fail(f"Firmware not present at {fw_path}")
    return fw_path


class AppUsbAudDut(UaDut):
    def __init__(self, adapter_id, board, config, xflash=False, writeall=False):
        fw_path = get_firmware_path(board, config)

        self.winbuiltin = platform.system() == "Windows" and (config.startswith("1") or "_winbuiltin" in config)

        if board == "xk_216_mc":
            target = "XCORE-200-EXPLORER"
        else:
            target = "XCORE-AI-EXPLORER"

        if "old_tools" in config:
            # This is an existing config built with old tools and copied to a new name with _old_tools attached to the original name.
            # Get the original name
            config = config.split("_old_tools")[0]

        self.features = get_config_features(board, config)

        if xflash and writeall:
            # writeall = True is a special case where we want to write the binary file produced from xflash -o <bin> directly to the device
            # This is needed if xflash -o <bin> is run with a different tools version before the test and the test is required to write the binary file
            # directly to the device
            fw_path = Path(fw_path).with_suffix(".bin") # The output of xflash -o is required to be saved in a file with the same name as the .xe but with a .bin extension

        super().__init__(adapter_id, fw_path, self.features["pid"][0], self.features["chan_i"], self.features["chan_o"], winbuiltin=self.winbuiltin, xflash=xflash, writeall=writeall, target=target)

    def __enter__(self):
        super().__enter__()

        # DUT has enumerated, so can now set the required dev_name for xsig
        if platform.system() == "Darwin":
            self.dev_name = self.usb_name
        elif platform.system() == "Windows":
            self.dev_name = "ASIO4ALL v2" if self.winbuiltin else "XMOS USB Audio Device"

        return self


def get_xtag_dut(pytestconfig, board):
    return pytestconfig.getini(f"{board}_dut")


def get_xtag_dut_and_harness(pytestconfig, board):
    dut = pytestconfig.getini(f"{board}_dut")
    harness = pytestconfig.getini(f"{board}_harness")
    return dut, harness
