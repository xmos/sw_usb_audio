import pytest
import subprocess
import xtagctl
from pathlib import Path
import platform
import stat
import requests


@pytest.fixture(autouse=True)
def xtagctl_wrapper(request):
    # Find out which board is being tested
    if any('xk_216_mc' in kw for kw in request.keywords):
        dut_target = 'usb_audio_mc_xs2_dut'
        dut_harness = 'usb_audio_mc_xs2_harness'
    elif any('xk_evk_xu316' in kw for kw in request.keywords):
        dut_target = 'usb_audio_xcai_exp_dut'
        dut_harness = 'usb_audio_xcai_exp_harness'
    else:
        pytest.fail('Cannot identify board to test')

    with xtagctl.acquire(dut_target, dut_harness) as (adapter_dut, adapter_harness):
        yield adapter_dut, adapter_harness

        # Since multiple DUTs can be connected to one test host, the application running on the DUT must be
        # stopped when the test ends; this can be done using xgdb to break in to stop it running
        subprocess.check_output(['xgdb', f'--eval-command=connect --adapter-id {adapter_dut}', '--eval-command=quit'])


@pytest.fixture
def xsig():
    """ Gets xsig from projects network drive """

    xsig_path = Path(__file__).parent / "tools" / "xsig"
    if xsig_path.exists():
        return xsig_path

    platform_str = platform.system()
    if platform_str == "Darwin":
        xsig_url = "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/macos/xsig"
    elif platform_str == "Linux":
        xsig_url = "http://intranet.xmos.local/projects/usb_audio_regression_files/xsig/linux/xsig"
    else:
        pytest.fail(f"Unsupported platform {platform_str}")

    r = requests.get(xsig_url)
    with open(xsig_path, "wb") as f:
        f.write(r.content)
    xsig_path.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

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
