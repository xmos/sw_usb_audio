# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import platform
import pytest
import subprocess
import time
import tempfile

from usb_audio_test_utils import get_firmware_path, get_xtag_dut, xtc_version, stop_xrun_app
from conftest import get_config_features


class DfuTester:
    def __init__(self, pytestconfig, board):
        self.xtag_id = get_xtag_dut(pytestconfig, board)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop_xrun_app(self.xtag_id)


def get_bcd_version(vid, pid, timeout=10):
    """Gets the BCD Device version number for a connected USB device with the
    specified VID and PID

    TODO: Windows support
    """

    for _ in range(timeout):
        time.sleep(1)

        if platform.system() == "Darwin":
            ret = subprocess.run(
                ["system_profiler", "SPUSBDataType"],
                capture_output=True,
                check=True,
                text=True,
            )
            current_pid = None
            current_vid = None
            for i, line in enumerate(ret.stdout.splitlines()):
                if line.strip().startswith("Product ID:"):
                    current_pid = int(line.split()[2], 16)
                if line.strip().startswith("Vendor ID:"):
                    current_vid = int(line.split()[2], 16)
                if line.strip().startswith("Version"):
                    if current_pid == pid and current_vid == vid:
                        return line.split()[1].strip()
        elif platform.system() == "Linux":
            ret = subprocess.run(
                ["lsusb", "-vd", f"{hex(vid)}:{hex(pid)}"],
                capture_output=True,
                check=True,
                text=True,
            )
            for line in ret.stdout.splitlines():
                if line.strip().startswith("bcdDevice"):
                    version_str = line.split()[1]
                    return version_str.strip()

    pytest.fail(f"Failed to get device version after {timeout}s")


def get_dfu_bin_path(board, config):
    return (
        Path(__file__).parents[1]
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.bin"
    )


def create_dfu_bin(board, config):
    firmware_path = get_firmware_path(board, config)
    dfu_bin_path = get_dfu_bin_path(board, config)
    # Assume that XE was built with the same version of XTC Tools as used in this test
    version = xtc_version()
    subprocess.run(
        [
            "xflash",
            "--factory-version",
            f'{version["major"]}.{version["minor"]}',
            "--upgrade",
            "1",
            firmware_path,
            "-o",
            dfu_bin_path,
        ],
        check=True,
    )
    return dfu_bin_path


# Test cases are defined by a tuple of (board, initial config to xflash)
dfu_testcases = [
    ("xk_216_mc", "2AMi10o10xssxxx"),
    ("xk_316_mc", "2AMi10o10xssxxx"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
]


def dfu_uncollect(pytestconfig, board, config):
    # Not yet supported on Windows
    if platform.system() == "Windows":
        return True
    level = pytestconfig.getoption("level")
    if level == "smoke":
        return board in ["xk_216_mc", "xk_evk_xu316"]
    return False


@pytest.mark.uncollect_if(func=dfu_uncollect)
@pytest.mark.parametrize(["board", "config"], dfu_testcases)
def test_dfu(pytestconfig, xmosdfu, board, config):
    features = get_config_features(board, config)
    vid = 0x20B1
    pid = features["pid"]

    with DfuTester(pytestconfig, board) as dfu_test:
        # xflash the factory image for the initial version
        firmware = get_firmware_path(board, config)
        subprocess.run(
            ["xflash", "--adapter-id", dfu_test.xtag_id, "--factory", firmware], check=True
        )
        initial_version = get_bcd_version(vid, pid)
        exp_version1 = "99.01"
        exp_version2 = "99.02"

        # perform the first upgrade
        dfu_bin1 = create_dfu_bin(board, "upgrade1")
        subprocess.run([xmosdfu, f"{hex(pid)}", "--download", dfu_bin1], check=True)
        version = get_bcd_version(vid, pid)
        if version != exp_version1:
            pytest.fail(f"Unexpected version {version} after first upgrade")

        # perform the second upgrade
        dfu_bin2 = create_dfu_bin(board, "upgrade2")
        subprocess.run([xmosdfu, f"{hex(pid)}", "--download", dfu_bin2], check=True)
        version = get_bcd_version(vid, pid)
        if version != exp_version2:
            pytest.fail(f"Unexpected version {version} after second upgrade")

        with tempfile.NamedTemporaryFile() as tmpfile:
            subprocess.run([xmosdfu, f"{hex(pid)}", "--upload", tmpfile.name], check=True)
            version = get_bcd_version(vid, pid)
            if version != exp_version2:
                pytest.fail(f"Unexpected version {version} after reading upgrade image")

            subprocess.run([xmosdfu, f"{hex(pid)}", "--revertfactory"], check=True)
            version = get_bcd_version(vid, pid)
            if version != initial_version:
                pytest.fail(
                    f"After factory reset, version {version} didn't match initial {initial_version}"
                )

            subprocess.run([xmosdfu, f"{hex(pid)}", "--download", tmpfile.name], check=True)
            version = get_bcd_version(vid, pid)
            if version != exp_version2:
                pytest.fail(
                    f"Unexpected version {version} after writing the image that was read"
                )

        # Finish by reverting back to the factory image again
        subprocess.run([xmosdfu, f"{hex(pid)}", "--revertfactory"], check=True)
        version = get_bcd_version(vid, pid)
        if version != initial_version:
            pytest.fail(
                f"Version {version} didn't match initial {initial_version} after final factory reset"
            )
