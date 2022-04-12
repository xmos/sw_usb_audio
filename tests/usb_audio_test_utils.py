import sounddevice as sd
import pytest
import subprocess
import tempfile
import platform
from pathlib import Path
import time
import os
import stat
import re


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


def run_audio_command(outfile, exe, *args):
    """ Run any command that needs to capture audio

    'outfile' is a file that must be provided to store stdout

    NOTE: If running on macOS on Jenkins, the environment WILL NOT be inherited
    by the child process
    """

    # If we're running on macOS on Jenkins, we need microphone permissions
    # To do this, we put an executable script in the $HOME/exec_all directory
    # A script is running on the host machine to execute everything in that dir
    if platform.system() == "Darwin" and "JENKINS" in os.environ:
        # Create a shell script to run the exe
        with tempfile.NamedTemporaryFile("w+", delete=False, dir=Path.home() / "exec_all") as script_file:
            str_args = [str(a) for a in args]
            # fmt: off
            script_text = (
                "#!/bin/bash\n"
                f"{exe} {' '.join(str_args)} > {outfile.name}\n"
            )
            # fmt: on
            script_file.write(script_text)
            script_file.flush()
            Path(script_file.name).chmod(
                stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
            )
            return

    subprocess.Popen([exe, *args], stdout=outfile, text=True)


def mark_tests(level_mark, testcases):
    return [pytest.param(*tc, marks=level_mark) for tc in testcases]


def get_line_matches(lines, expected):
    matches = []
    for line in lines:
        match = re.search(expected, line)
        if match:
            matches.append(match.group(1))

    return matches


def check_analyzer_output(analyzer_output, xsig_config):
    """ Verify that the output from xsig is correct """

    failures = []
    # Check for any errors
    for line in analyzer_output:
        if re.match(".*ERROR|.*error|.*Error|.*Problem", line):
            failures.append(line)

    num_chans = len(xsig_config)
    analyzer_channels = [[] for _ in range(num_chans)]
    for line in analyzer_output:
        match = re.search(r'^Channel (\d+):', line)
        if not match:
            continue

        channel = int(match.group(1))
        if channel not in range(num_chans):
            failures.append(f'Invalid channel number {channel}')
            continue

        analyzer_channels[channel].append(line)

        if re.match(r'Channel \d+: Lost signal', line):
            failures.append(line)

    for idx, channel_config in enumerate(xsig_config):
        if channel_config[0] == 'volcheck':
            vol_changes = get_line_matches(analyzer_channels[idx], r'.*Volume change by (-?\d+)')

            if len(vol_changes) < 2:
                failures.append(f'Initial volume and initial change not found on channel {idx}')
                continue

            initial_volume = int(vol_changes.pop(0))
            initial_change = int(vol_changes.pop(0))
            if initial_change >= 0:
                failures.append(f'Initial change is not negative on channel {idx}: {initial_change}')
            initial_change = abs(initial_change)
            exp_vol_changes = [1.0, -0.5, 0.5]
            if len(vol_changes) != len(exp_vol_changes):
                failures.append(f'Unexpected number of volume changes on channel {idx}: {vol_changes}')
                continue

            for vol_change, exp_ratio in zip(vol_changes, exp_vol_changes):
                expected = initial_change * exp_ratio
                if abs(int(vol_change) - expected) > 2:
                    failures.append(f'Volume change not as expected on channel {idx}: actual {vol_change}, expected {expected}')

        elif channel_config[0] == 'sine':
            exp_freq = channel_config[1]
            chan_freqs = get_line_matches(analyzer_channels[idx], r'^Channel \d+: Frequency (\d+)')
            if not len(chan_freqs):
                failures.append(f'No signal seen on channel {idx}')
            for freq in chan_freqs:
                if int(freq) != exp_freq:
                    failures.append(f'Incorrect frequency on channel {idx}; got {freq}, expected {exp_freq}')
        else:
            failures.append(f'Invalid channel config {channel_config}')

    if len(failures) > 0:
        pytest.fail('Checking analyser output failed:\n' + '\n'.join(failures))
