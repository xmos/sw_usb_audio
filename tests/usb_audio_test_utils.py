import sounddevice as sd
import pytest
import sh
import tempfile
import platform
from pathlib import Path
import time
import os
import stat


def product_str_from_board_config(board, config):
    if board == 'xk_216_mc':
        if config.startswith('1'):
            return 'XMOS xCORE-200 MC (UAC1.0)'
        elif config.startswith('2'):
            return 'XMOS xCORE-200 MC (UAC2.0)'
        else:
            pytest.fail(f"Unrecognised config {config} for {board}")
    elif board == 'xk_evk_xu316':
        if config.startswith('1'):
            return 'XMOS xCORE (UAC1.0)'
        elif config.startswith('2'):
            return 'XMOS xCORE (UAC2.0)'
        else:
            pytest.fail(f"Unrecognised config {config} for {board}")
    else:
        pytest.fail(f"Unrecognised board {board}")


def wait_for_portaudio(board, config, timeout=10):
    prod_str = product_str_from_board_config(board, config)

    for _ in range(timeout):
        time.sleep(1)

        # sounddevice must be terminated and re-initialised to get updated device info
        sd._terminate()
        sd._initialize()
        sd_devs = [sd_dev['name'] for sd_dev in sd.query_devices()]
        if prod_str in sd_devs:
            return

    pytest.fail(f"Device not available via portaudio in {timeout}s")


def get_firmware_path_harness(board, config=None):
    xe_name = f"app_audio_analyzer_{board}_{config}.xe" if config else f"app_audio_analyzer_{board}.xe"
    return Path(__file__).parents[2] / "sw_audio_analyzer" / f"app_audio_analyzer_{board}" / "bin" / xe_name


def get_firmware_path(board, config):
    return Path(__file__).parents[1] / f"app_usb_aud_{board}" / "bin" / config / f"app_usb_aud_{board}_{config}.xe"


def run_audio_command(runtime, exe, *args):
    """ Run any command that needs to capture audio

    NOTE: If running on macOS on Jenkins, the environment WILL NOT be inherited
    by the child process
    """

    # If we're running on macOS on Jenkins, we need microphone permissions
    # To do this, we put an executable script in the $HOME/exec_all directory
    # A script is running on the host machine to execute everything in that dir
    if platform.system() == "Darwin":
        if "JENKINS" in os.environ:
            # Create a shell script to run the exe
            with tempfile.NamedTemporaryFile("w+", delete=True) as tmpfile:
                with tempfile.NamedTemporaryFile("w+", delete=False, dir=Path.home() / "exec_all") as script_file:
                    str_args = [str(a) for a in args]
                    # fmt: off
                    script_text = (
                        "#!/bin/bash\n"
                        f"{exe} {' '.join(str_args)} > {tmpfile.name}\n"
                    )
                    # fmt: on
                    script_file.write(script_text)
                    script_file.flush()
                    Path(script_file.name).chmod(
                        stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
                    )
                    time.sleep(runtime + 2)
                    stdout = tmpfile.read()
                    return stdout

    stdout = sh.Command(exe)(*args, _timeout=runtime)
    return stdout


def mark_tests(level_mark, testcases):
    return [pytest.param(*tc, marks=level_mark) for tc in testcases]
