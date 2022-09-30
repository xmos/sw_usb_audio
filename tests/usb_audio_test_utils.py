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
import socket


def product_str_from_board_config(board, config):
    if board == 'xk_216_mc':
        if config.startswith('1'):
            return 'XMOS xCORE-200 MC (UAC1.0)'
        elif config.startswith('2'):
            return 'XMOS xCORE-200 MC (UAC2.0)'
    elif board == 'xk_316_mc':
        if config.startswith('1'):
            return 'XMOS xCORE.ai MC (UAC1.0)'
        elif config.startswith('2'):
            return 'XMOS xCORE.ai MC (UAC2.0)'
    elif board == 'xk_evk_xu316':
        if config.startswith('1'):
            return 'XMOS xCORE (UAC1.0)'
        elif config.startswith('2'):
            return 'XMOS xCORE (UAC2.0)'
    else:
        pytest.fail(f"Unrecognised board {board}")

    pytest.fail(f"Unrecognised config {config} for {board}")


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

    pytest.fail(f"Device ({prod_str}) not available via portaudio in {timeout}s")


def get_firmware_path_harness(board, config=None):
    xe_name = f"app_audio_analyzer_{board}_{config}.xe" if config else f"app_audio_analyzer_{board}.xe"
    bin_dir = Path(__file__).parents[2] / "sw_audio_analyzer" / f"app_audio_analyzer_{board}" / "bin"
    if config:
        bin_dir = bin_dir / f"{config}"
    fw_path = bin_dir / xe_name
    if not fw_path.exists():
        pytest.fail(f"Harness firmware not present at {fw_path}")
    return fw_path


def get_firmware_path(board, config):
    fw_path = Path(__file__).parents[1] / f"app_usb_aud_{board}" / "bin" / config / f"app_usb_aud_{board}_{config}.xe"
    if not fw_path.exists():
        pytest.fail(f"Firmware not present at {fw_path}")
    return fw_path


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

        elif channel_config[0] == 'ramp':
            exp_ramp = channel_config[1]
            ramps = get_line_matches(analyzer_channels[idx], r'.*step = (-?\d+)')

            if len(ramps) == 0:
                failures.append(f"No ramp seen on channel {idx}")

            for ramp in ramps:
                if int(ramp) != exp_ramp:
                    failures.append(f"Incorrect ramp on channel {idx}: got {ramp}, expected {exp_ramp}")

            for line in analyzer_channels[idx]:
                if re.match(".*discontinuity", line):
                    failures.append(line)

        elif channel_config[0] == 'zero':
            if len(analyzer_channels[idx]):
                failures.append(analyzer_channels[idx])

        else:
            failures.append(f'Invalid channel config {channel_config}')

    if len(failures) > 0:
        pytest.fail('Checking analyser output failed:\n' + '\n'.join(failures))


# Get an available port number by binding a socket then closing it (assuming nothing else takes it before it's used by xrun)
def get_xscope_port_number():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
    return port


def wait_for_xscope_port(port, timeout=10):
    for _ in range(timeout):
        time.sleep(1)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("localhost", port))
            except OSError:
                # Failed to bind, so xrun has this port open and is ready to use
                return

    pytest.fail(f'xscope port {port} not ready after {timeout}s')
