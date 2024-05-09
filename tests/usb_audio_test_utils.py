import configparser
import pytest
import subprocess
import tempfile
import platform
from pathlib import Path
import time
import os
import stat
import re
import shutil
import socket

from conftest import get_config_features


def use_windows_builtin_driver(board, config):
    # Use the builtin driver for:
    #  - configs with the"_winbuiltin" keyword
    #  - our UAC 1 PID is not supported by the Thesycon driver
    if config.startswith("1"):
        return True
    if "_winbuiltin" in config:
        return True
    return False


def product_str_from_board_config(board, config):
    if platform.system() == "Windows" and not use_windows_builtin_driver(board, config):
        return "XMOS USB Audio Device"

    if board == "xk_216_mc":
        if config.startswith("1"):
            return "XMOS xCORE-200 MC (UAC1.0)"
        elif config.startswith("2"):
            return "XMOS xCORE-200 MC (UAC2.0)"
    elif board == "xk_316_mc":
        if config.startswith("1"):
            return "XMOS xCORE.ai MC (UAC1.0)"
        elif config.startswith("2"):
            return "XMOS xCORE.ai MC (UAC2.0)"
    elif board == "xk_evk_xu316":
        if config.startswith("1"):
            return "XMOS xCORE (UAC1.0)"
        elif config.startswith("2"):
            return "XMOS xCORE (UAC2.0)"
    else:
        pytest.fail(f"Unrecognised board {board}")

    pytest.fail(f"Unrecognised config {config} for {board}")


def query_device_found(name):
    binary_name = "xsig.exe" if platform.system() == "Windows" else "xsig"
    xsig_bin = Path(__file__).parent / "tools" / binary_name
    ret = subprocess.run(
        [xsig_bin, "--list-devices"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    for line in ret.stdout.split("\n"):
        if name in line:
            return True

    return False


def wait_for_portaudio(board, config, adapter_id):
    timeout = 30
    prod_str = product_str_from_board_config(board, config)

    for _ in range(timeout):
        time.sleep(1)

        if query_device_found(prod_str):
            return prod_str

    fail_str = f"Device ({prod_str}) not enumerated after {timeout}s\n"

    # Device doesn't appear to have started, so dump the state of the xcore
    firmware = get_firmware_path(board, config)
    ret = subprocess.run(
        ["xrun", "--adapter-id", adapter_id, "--dump-state", firmware],
        text=True,
        timeout=10,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    fail_str += "Register and thread state of the xcore device\n"
    fail_str += "\n".join(ret.stdout.splitlines())
    pytest.fail(fail_str)


def get_firmware_path(board, config):
    # XE can be called app_usb_aud_{board}.xe or app_usb_aud_{board}_{config}.xe
    xe_name = f"app_usb_aud_{board}_{config}.xe"
    fw_path_base = Path(__file__).parents[1] / f"app_usb_aud_{board}" / "bin" / config
    fw_path = fw_path_base / xe_name
    if not fw_path.exists():
        xe_name = f"app_usb_aud_{board}.xe"
        fw_path = fw_path_base / xe_name
        if not fw_path.exists():
            pytest.fail(f"Firmware not present at {fw_path_base}")
    return fw_path


def get_line_matches(lines, expected):
    matches = []
    for line in lines:
        match = re.search(expected, line)
        if match:
            matches.append(match.group(1))

    return matches


def check_analyzer_output(analyzer_output, xsig_config):
    """Verify that the output from xsig is correct"""

    failures = []
    # Check for any errors
    for line in analyzer_output:
        if re.match(".*(?<!no )(error|problem)", line.lower()):
            failures.append(line)

    num_chans = len(xsig_config)
    analyzer_channels = [[] for _ in range(num_chans)]
    for line in analyzer_output:
        match = re.search(r"^Channel (\d+):", line)
        if not match:
            continue

        channel = int(match.group(1))
        if channel not in range(num_chans):
            failures.append(f"Invalid channel number {channel}")
            continue

        analyzer_channels[channel].append(line)

        if re.match(r"Channel \d+: Lost signal", line):
            failures.append(line)

    for idx, channel_config in enumerate(xsig_config):
        if channel_config[0] == "volcheck":
            vol_changes = get_line_matches(
                analyzer_channels[idx], r".*Volume change by (-?\d+)"
            )

            if len(vol_changes) < 2:
                failures.append(
                    f"Initial volume and initial change not found on channel {idx}"
                )
                continue

            _ = int(vol_changes.pop(0))
            initial_change = int(vol_changes.pop(0))
            if initial_change >= 0:
                failures.append(
                    f"Initial change is not negative on channel {idx}: {initial_change}"
                )
            initial_change = abs(initial_change)
            exp_vol_changes = [1.0, -0.5, 0.5]
            if len(vol_changes) != len(exp_vol_changes):
                failures.append(
                    f"Unexpected number of volume changes on channel {idx}: {vol_changes}"
                )
                continue

            for vol_change, exp_ratio in zip(vol_changes, exp_vol_changes):
                expected = initial_change * exp_ratio
                if abs(int(vol_change) - expected) > 2:
                    failures.append(
                        f"Volume change not as expected on channel {idx}: actual {vol_change}, expected {expected}"
                    )

        elif channel_config[0] == "sine":
            exp_freq = channel_config[1]
            chan_freqs = get_line_matches(
                analyzer_channels[idx], r"^Channel \d+: Frequency (\d+)"
            )
            if not len(chan_freqs):
                failures.append(f"No signal seen on channel {idx}")
            for freq in chan_freqs:
                if int(freq) != exp_freq:
                    failures.append(
                        f"Incorrect frequency on channel {idx}; got {freq}, expected {exp_freq}"
                    )

        elif channel_config[0] == "ramp":
            exp_ramp = channel_config[1]
            ramps = get_line_matches(analyzer_channels[idx], r".*step = (-?\d+)")

            if len(ramps) == 0:
                failures.append(f"No ramp seen on channel {idx}")

            for ramp in ramps:
                if int(ramp) != exp_ramp:
                    failures.append(
                        f"Incorrect ramp on channel {idx}: got {ramp}, expected {exp_ramp}"
                    )

            for line in analyzer_channels[idx]:
                if re.match(".*discontinuity", line):
                    failures.append(line)

        elif channel_config[0] == "zero":
            if len(analyzer_channels[idx]):
                for line in analyzer_channels[idx]:
                    failures.append(line)

        else:
            failures.append(f"Invalid channel config {channel_config}")

    return failures


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

    pytest.fail(f"xscope port {port} not ready after {timeout}s")


def xtc_version():
    version_re = r"XTC version: (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    ret = subprocess.run(["xcc", "--version"], capture_output=True, text=True)
    match = re.search(version_re, ret.stdout)
    if not match:
        pytest.fail(f"Unable to get XTC Tools version: stdout={ret.stdout}")
    return match.groupdict()


def split_board_config(board_config):
    return tuple(board_config.split("-", maxsplit=1))


def get_xtag_dut(pytestconfig, board):
    return pytestconfig.getini(f"{board}_dut")


def get_xtag_dut_and_harness(pytestconfig, board):
    dut = pytestconfig.getini(f"{board}_dut")
    harness = pytestconfig.getini(f"{board}_harness")
    return dut, harness


# Stop an application that was run using xrun by breaking in with xgdb
# Allow a long timeout here because sometimes an XTAG can get stuck in a USB transaction when xrun
# is killed, and this connect via xgdb can recover it but it takes a while to reboot the XTAG
def stop_xrun_app(adapter_id):
    subprocess.run(
        ["xgdb", "-ex", f"connect --adapter-id {adapter_id}", "-ex", "quit"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=120,
    )


def get_volcontrol_path():
    base_dir = Path(__file__).parent / "tools" / "volcontrol"
    if platform.system() == "Windows":
        app_path = base_dir / "x64" / "Release" / "volcontrol.exe"
    else:
        app_path = base_dir / "build" / "volcontrol"
    if not app_path.exists():
        pytest.fail(f"volcontrol not present at {app_path}")
    return app_path


def get_xscope_controller_path():
    base_dir = (
        Path(__file__).parents[2] / "sw_audio_analyzer" / "host_xscope_controller"
    )
    platform_str = platform.system()
    if platform_str == "Windows":
        app_path = base_dir / "bin_windows" / "xscope_controller.exe"
    elif platform_str == "Darwin":
        app_path = base_dir / "bin_macos" / "xscope_controller"
    else:
        pytest.fail(f"xscope_controller not supported on platform {platform_str}")

    if not app_path.exists():
        pytest.fail(f"xscope_controller not present at {app_path}")
    return app_path


# Windows host applications require the tusbaudio driver GUID, which can be found in custom.ini
# in the driver installation directory
def get_tusb_guid():
    ini_path = (
        Path(os.environ["PROGRAMFILES"])
        / "XMOS"
        / "USB Audio Device Driver"
        / "x64"
        / "custom.ini"
    )
    if not ini_path.exists():
        pytest.fail(
            f"tusbaudio SDK custom.ini not found in expected location: {ini_path}"
        )

    with open(ini_path, "r") as f:
        config = configparser.ConfigParser()
        config.read_file(f)
        try:
            guid = config.get("DriverInterface", "InterfaceGUID")
            return guid
        except (configparser.NoSectionError, configparser.NoOptionError):
            pytest.fail("Could not find InterfaceGUID in custom.ini")


def stream_format_setup(direction, samp_freq, num_chans, bit_depth):
    cmd = [get_volcontrol_path()]
    if platform.system() == "Windows":
        cmd.append(f"-g{get_tusb_guid()}")
    cmd += ["--set-format", direction, f"{samp_freq}", f"{num_chans}", f"{bit_depth}"]
    ret = subprocess.run(cmd, timeout=30, capture_output=True, text=True)
    if ret.returncode != 0:
        pytest.fail(f"failed to setup stream format: {direction}, {samp_freq} fs, {num_chans} channels, {bit_depth} bit\n{ret.stdout}\n{ret.stderr}")


class AudioAnalyzerHarness:
    """
    Run the audio analyzer harness

    The xscope parameter can be None, "io" or "app". If None, xrun does not remain
    attached after starting the application. If "io", xrun remains attached and
    stdout/stderr is collected. If "app", xrun opens up a port and waits for another
    application to connect; the application that wants to connect should use the
    port number stored in the xscope_port member of this class.
    """

    def __init__(self, adapter_id, board="xcore200_mc", config=None, xscope=None):
        self.adapter_id = adapter_id
        xe_name = (
            f"app_audio_analyzer_{board}_{config}.xe"
            if config
            else f"app_audio_analyzer_{board}.xe"
        )
        bin_dir = (
            Path(__file__).parents[2]
            / "sw_audio_analyzer"
            / f"app_audio_analyzer_{board}"
            / "bin"
        )
        if config:
            bin_dir = bin_dir / f"{config}"
        self.harness_firmware = bin_dir / xe_name
        if not self.harness_firmware.exists():
            pytest.fail(f"Harness firmware not present at {self.harness_firmware}")
        if xscope and xscope not in ["app", "io"]:
            pytest.fail(f"Error: invalid xscope option value {xscope}")
        self.xscope = xscope
        self.xscope_port = None
        self.proc = None

    def __enter__(self):
        xrun_cmd = ["xrun", "--adapter-id", self.adapter_id]
        if self.xscope == "app":
            self.xscope_port = get_xscope_port_number()
            xrun_cmd.append("--xscope-port")
            xrun_cmd.append(f"localhost:{self.xscope_port}")
        elif self.xscope == "io":
            xrun_cmd.append("--xscope")
        xrun_cmd.append(self.harness_firmware)

        if self.xscope:
            # If attaching via xscope, store the Popen object to terminate it later
            self.proc = subprocess.Popen(
                xrun_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            # Wait to allow the xrun command to start running
            time.sleep(5)

            if self.xscope == "app":
                wait_for_xscope_port(self.xscope_port)
        else:
            # If not attaching via xscope, wait for the xrun command to complete
            ret = subprocess.run(xrun_cmd, capture_output=True, text=True, timeout=60)
            if ret.returncode != 0:
                pytest.fail(
                    f"Failed to launch audio analyzer, cmd {xrun_cmd}\n"
                    + f"stdout:\n{ret.stdout}\n"
                    + f"stderr:\n{ret.stderr}\n"
                )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def terminate(self):
        if self.proc and self.proc.poll() is None:
            # Due to a bug in Tools 15.1.4, terminating xrun leaves xgdb running.
            # Kill all xgdb processes, since the xgdb process ID is unknown.
            self.proc.terminate()
            time.sleep(1)
            if platform.system() == "Windows":
                kill_cmd = ["taskkill", "/F", "/IM", "xgdb.exe"]
            else:
                kill_cmd = ["pkill", "-9", "xgdb"]
            subprocess.run(
                kill_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
        stop_xrun_app(self.adapter_id)

    def get_output(self):
        if not self.proc:
            return []
        try:
            out, _ = self.proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pytest.fail("Error: timeout getting audio analyzer output")
        return out.decode().splitlines()


class XrunDut:
    """
    Run a USB Audio application on a device

    A USB Audio application, chosen based on the board and config parameters, is
    run on the device accessible via the XTAG given by the adapter_id parameter.

    There is a delay after starting the application to wait for it to appear as a
    PortAudio device. Then the device_name class member can be used by audio
    software to use this particular device.
    """

    def __init__(self, adapter_id, board, config):
        self.adapter_id = adapter_id
        self.board = board
        self.config = config
        features = get_config_features(board, config)
        self.pid = features["pid"]
        self.dev_name = None

    def __enter__(self):
        firmware = get_firmware_path(self.board, self.config)
        subprocess.run(["xrun", "--adapter-id", self.adapter_id, firmware], timeout=30)
        self.dev_name = wait_for_portaudio(self.board, self.config, self.adapter_id)
        if platform.system() == "Windows" and use_windows_builtin_driver(
            self.board, self.config
        ):
            # Select ASIO4ALL as device for built-in driver testing (cannot wait for this device
            # name in wait_for_portaudio because it is always present)
            self.dev_name = "ASIO4ALL v2"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop_xrun_app(self.adapter_id)

        # If usbdeview program is present on Windows, uninstall the device to force
        # re-enumeration next time and avoid caching of device features by the OS
        if platform.system() == "Windows":
            usbdeview_path = shutil.which("usbdeview")
            if usbdeview_path:
                subprocess.run(
                    [
                        usbdeview_path,
                        "/RunAsAdmin",
                        "/remove_by_pid",
                        f"0x20b1;{hex(self.pid)}",
                    ],
                    timeout=10,
                )


class XsigProcess:
    """
    Super-class to run the xsig analyzer/signal generator

    In general, this class shouldn't be used directly; instead use XsigInput or XsigOutput.

    The application requires a sample rate (fs), duration in seconds (can be zero for indefinite
    runtime), a configuration file and the name of the audio device to use.
    """

    def __init__(self, fs, duration, cfg_file, dev_name, ident=None):
        self.duration = 0 if duration is None else duration
        binary_name = "xsig.exe" if platform.system() == "Windows" else "xsig"
        self.xsig_dir = Path(__file__).parent / "tools"
        xsig = self.xsig_dir / binary_name
        if not xsig.exists():
            pytest.fail(f"xsig binary not present in {xsig.parent}")
        self.xsig_cmd = [
            xsig,
            f"{fs}",
            f"{self.duration * 1000}",
            cfg_file,
            "--device",
            dev_name,
        ]
        self.proc = None
        self.output_file = None
        self.ident = ident

    def __enter__(self):
        self.proc = subprocess.Popen(
            self.xsig_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=self.xsig_cmd[0].parent,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proc and (self.proc.poll() is None):
            self.proc.terminate()

        # Rename any glitch data csv files
        if self.ident:
            csv_files = self.xsig_dir.glob("*.csv")
            for file in csv_files:
                filename = file.name

                # Glitch data files are called glitch.<chan>.sig.csv and glitch.<chan>.fft.csv
                # Add in the ident string to make the filename unique for the test run
                artifact_re = r"^(glitch\.)\d.*\.csv$"
                match = re.search(artifact_re, filename)
                if match:
                    pre = match.group(1)
                    target = self.xsig_dir / f"{pre}{self.ident}.{filename[len(pre):]}"
                    file.rename(target)

    def get_output(self):
        try:
            out, _ = self.proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pytest.fail("Error: timeout getting xsig output")
        return out.decode().splitlines()


class XsigInput(XsigProcess):
    """
    Xsig input class

    This class contains logic that is specific to running an instance of xsig for an input test.

    As a workaround for MacOS privacy restrictions, a Python script can be created which will run
    the xsig command with a timeout; this is executed by a separate script running on the host.
    """

    def __enter__(self):
        if (
            platform.system() == "Darwin"
            and os.environ.get("USBA_MAC_PRIV_WORKAROUND", None) == "1"
        ):
            self.output_file = tempfile.NamedTemporaryFile(mode="w+")
            # Create a Python script to run the xsig command
            with tempfile.NamedTemporaryFile(
                "w+", delete=False, dir=Path.home() / "exec_all", suffix=".py"
            ) as script_file:
                # fmt: off
                script_text = (
                    'import subprocess\n'
                    'from pathlib import PosixPath\n'
                    f'with open("{self.output_file.name}", "w+") as f:\n'
                    '    try:\n'
                    f'        ret = subprocess.run({self.xsig_cmd}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout={self.duration+5}, cwd=PosixPath("{self.xsig_dir}"))\n'
                    f'    except subprocess.TimeoutExpired:\n'
                    f'        f.write("Timeout running command: {self.xsig_cmd}")\n'
                    '    else:\n'
                    '        f.write(ret.stdout.decode())\n'
                )
                # fmt: on
                script_file.write(script_text)
                script_file.flush()
                Path(script_file.name).chmod(
                    stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC
                )
            return self
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proc is None:
            del self.output_file
        super().__exit__(exc_type, exc_val, exc_tb)

    def get_output(self):
        if (
            platform.system() == "Darwin"
            and os.environ.get("USBA_MAC_PRIV_WORKAROUND", None) == "1"
        ):
            self.output_file.seek(0)
            return [line.strip() for line in self.output_file.readlines()]
        return super().get_output()


class XsigOutput(XsigProcess):
    """
    Xsig output class

    No output-specific logic is required, but this class should still be used instead of
    XsigProcess as it makes the direction of the test-code more obvious to the reader.
    """

    pass
