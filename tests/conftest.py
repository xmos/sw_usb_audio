import pytest
import subprocess
from pathlib import Path
import platform
import stat
import requests


# XTAG IDs for the boards in the test setup can be hard-coded here to avoid having to use the
# pytest command-line options for a fixed local setup.
XK_216_MC_DUT = None
XK_216_MC_HARNESS = None
XK_EVK_XU316_DUT = None
XK_EVK_XU316_HARNESS = None


def pytest_addoption(parser):
    parser.addoption("--xk-216-mc-dut", action="store", default=XK_216_MC_DUT)
    parser.addoption("--xk-216-mc-harness", action="store", default=XK_216_MC_HARNESS)
    parser.addoption("--xk-evk-xu316-dut", action="store", default=XK_EVK_XU316_DUT)
    parser.addoption("--xk-evk-xu316-harness", action="store", default=XK_EVK_XU316_HARNESS)


@pytest.fixture(autouse=True)
def xtag_wrapper(pytestconfig, request):
    # Find out which board is being tested
    if any("xk_216_mc" in kw for kw in request.keywords):
        board = "xk_216_mc"
        adapter_dut = pytestconfig.getoption("xk_216_mc_dut")
        adapter_harness = pytestconfig.getoption("xk_216_mc_harness")
    elif any("xk_evk_xu316" in kw for kw in request.keywords):
        board = "xk_evk_xu316"
        adapter_dut = pytestconfig.getoption("xk_evk_xu316_dut")
        adapter_harness = pytestconfig.getoption("xk_evk_xu316_harness")
    else:
        pytest.fail("Cannot identify board to test")

    if not all([adapter_dut, adapter_harness]):
        pytest.skip(f"Both DUT and harness for {board} must be specified")

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
