import pytest
import subprocess
import xtagctl

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
