import pytest
import subprocess
from pathlib import Path
import platform
import stat
import requests


def pytest_addoption(parser):
    parser.addini("xk_216_mc_dut", help="XTAG ID for xk_216_mc DUT")
    parser.addini("xk_216_mc_harness", help="XTAG ID for xk_216_mc harness")
    parser.addini("xk_316_mc_dut", help="XTAG ID for xk_316_mc DUT")
    parser.addini("xk_316_mc_harness", help="XTAG ID for xk_316_mc harness")
    parser.addini("xk_evk_xu316_dut", help="XTAG ID for xk_evk_xu316 DUT")
    parser.addini("xk_evk_xu316_harness", help="XTAG ID for xk_evk_xu316 harness")


boards = ["xk_216_mc", "xk_316_mc", "xk_evk_xu316"]

# Dictionary indexed by board name, with each entry being the tuple of XTAG IDs for
# the DUT and harness for that board, (None, None) if XTAGs for board not provided.
xtag_dut_harness = {}


def pytest_collection_modifyitems(config, items):
    # Populate the xtag_dut_harness dictionary with the XTAG IDs that were set
    # in pytest.ini or overridden on the command-line
    for board in boards:
        dut = config.getini(f"{board}_dut")
        harness = config.getini(f"{board}_harness")
        xtag_dut_harness[board] = (dut, harness)

    selected = []
    deselected = []

    # Deselect testcases which use hardware that doesn't have an XTAG ID
    for item in items:
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
    subprocess.check_output(["xgdb", f"--eval-command=connect --adapter-id {adapter_dut}", "--eval-command=quit"])


@pytest.fixture
def xsig():
    xsig_path = Path(__file__).parent / "tools" / "xsig"
    if not xsig_path.exists():
        pytest.fail(f"xsig binary not present in {xsig_path.parent}")

    return xsig_path


@pytest.fixture
def xmosdfu():
    """Gets xmosdfu from projects network drive """

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
