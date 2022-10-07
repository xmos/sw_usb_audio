import pytest
import subprocess
from pathlib import Path
import platform
import stat
import requests
import re


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


def parse_features(config):
    max_analogue_chans = 8

    config_re = r"^(?P<uac>[12])(?P<sync_mode>[AS])(?P<slave>[MS])i(?P<chan_i>\d+)o(?P<chan_o>\d+)(?P<midi>[mx])(?P<spdif_i>[sx])(?P<spdif_o>[sx])(?P<adat_i>[ax])(?P<adat_o>[ax])(?P<dsd>[dx])(?P<tdm8>(_tdm8)?)"
    match = re.search(config_re, config)
    if not match:
        pytest.exit(f"Unable to parse features from {config}")

    # Form dictionary of features then convert items to integers or boolean as required
    features = match.groupdict()
    for k in ["uac", "chan_i", "chan_o"]:
        features[k] = int(features[k])
    for k in ["midi", "spdif_i", "spdif_o", "adat_i", "adat_o", "dsd", "tdm8"]:
        features[k] = features[k] not in ["", "x"]

    features["slave"] = features["slave"] == "S"

    # Set the number of analogue channels
    features["analogue_i"] = min(features["chan_i"], max_analogue_chans)
    features["analogue_o"] = min(features["chan_o"], max_analogue_chans)
    if "noi2s" in config:
        # Force analogue channels to zero
        features["analogue_i"] = 0
        features["analogue_o"] = 0

    # Set the maximum sample rate frequency
    if config == "1AMi8o2xxxxxx":
        features["max_freq"] = 44100
    elif features["uac"] == 1:
        if features["chan_i"] and features["chan_o"]:
            features["max_freq"] = 48000
        else:
            features["max_freq"] = 96000
    elif features["chan_i"] >= 32 or features["chan_o"] >= 32:
        features["max_freq"] = 48000
    elif features["chan_i"] >= 16 or features["chan_o"] >= 16:
        features["max_freq"] = 96000
    elif features["tdm8"]:
        features["max_freq"] = 96000
    else:
        features["max_freq"] = 192000

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
        partial_configs = [config for config in configs if config not in full_configs]
        for config in configs:
            global board_configs
            features = parse_features(config)
            # Mark the relevant configs for partial testing only
            features["partial"] = config in partial_configs
            board_configs[f"{board}-{config}"] = features


def list_configs():
    return board_configs.keys()


def get_config_features(board_config):
    return board_configs[board_config]


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
            if func(config.getoption("level"), **item.callspec.params):
                deselected.append(item)
                continue

        xtags = (None, None)
        for board in boards:
            if any(board in kw for kw in item.keywords):
                xtags = xtag_dut_harness[board]
                break

        if all([*xtags]):
            selected.append(item)
        else:
            deselected.append(item)

    config.hook.pytest_deselected(items=deselected)
    items[:] = selected


@pytest.fixture(autouse=True)
def xtag_wrapper(pytestconfig, request):
    for board in boards:
        if any(board in kw for kw in request.keywords):
            (adapter_dut, adapter_harness) = xtag_dut_harness[board]
            break

    yield adapter_dut, adapter_harness

    # Since multiple DUTs can be connected to one test host, the application running on the DUT must be
    # stopped when the test ends; this can be done using xgdb to break in to stop it running
    subprocess.check_output(
        [
            "xgdb",
            f"--eval-command=connect --adapter-id {adapter_dut}",
            "--eval-command=quit",
        ]
    )


@pytest.fixture
def xsig():
    xsig_path = Path(__file__).parent / "tools" / "xsig"
    if not xsig_path.exists():
        pytest.fail(f"xsig binary not present in {xsig_path.parent}")

    return xsig_path


@pytest.fixture
def xmosdfu():
    """Gets xmosdfu from projects network drive"""

    xmosdfu_path = Path(__file__).parent / "tools" / "xmosdfu"
    if xmosdfu_path.exists():
        return xmosdfu_path

    platform_str = platform.system()
    if platform_str == "Darwin":
        xmosdfu_url = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/macos/xmosdfu"
    elif platform_str == "Linux":
        xmosdfu_url = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/linux/xmosdfu"
    else:
        pytest.fail(f"Unsupported platform {platform_str}")

    r = requests.get(xmosdfu_url)
    with open(xmosdfu_path, "wb") as f:
        f.write(r.content)
    xmosdfu_path.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    return xmosdfu_path
