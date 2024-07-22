# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import platform
import pytest
import subprocess
import time
import os
import re
import stat
import urllib.request

from usb_audio_test_utils import (
    get_firmware_path,
    get_xtag_dut,
    xtc_version,
    stop_xrun_app,
    get_tusb_guid,
)
from conftest import get_config_features


# Common options to subprocess: capture output as text, timeout after 300s
common_opts = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.STDOUT,
    "text": True,
    "timeout": 300,
}


class DfuTester:
    def __init__(self, pytestconfig, board, config):
        self.upload_bin = Path(__file__).parent / "upload0.bin"
        self.xtag_id = get_xtag_dut(pytestconfig, board)
        features = get_config_features(board, config)
        self.pid = features["pid"]
        platform_str = platform.system()
        if platform_str == "Windows":
            self.driver_guid = get_tusb_guid()
            self.dfu_app = (
                Path(os.environ["PROGRAMFILES"])
                / "XMOS"
                / "tusbaudiosdk"
                / "bin"
                / "Debug"
                / "x64"
                / "dfucons.exe"
            )
            if not self.dfu_app.exists():
                pytest.fail(f"dfucons.exe not found in location: {self.dfu_app}")
        elif platform_str in ["Darwin", "Linux"]:
            xmosdfu_path = Path(__file__).parent / "tools" / "xmosdfu"
            if not xmosdfu_path.exists():
                pytest.fail(f"xmosdfu not found in location: {xmosdfu_path}")
            self.dfu_app = xmosdfu_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.upload_bin.exists():
            self.upload_bin.unlink()
        stop_xrun_app(self.xtag_id)

    def get_bcd_version(self):
        timeout = 30
        vid = 0x20B1

        if platform.system() == "Windows":
            # Initially the version number can be reported unchanged after
            # a DFU download, so wait briefly before checking
            time.sleep(5)

        for _ in range(timeout):
            time.sleep(1)

            platform_str = platform.system()
            if platform_str == "Darwin":
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
                        if current_pid == self.pid and current_vid == vid:
                            return line.split()[1].strip()
            elif platform_str == "Linux":
                ret = subprocess.run(
                    ["lsusb", "-vd", f"{hex(vid)}:{hex(self.pid)}"],
                    capture_output=True,
                    check=True,
                    text=True,
                )
                for line in ret.stdout.splitlines():
                    if line.strip().startswith("bcdDevice"):
                        version_str = line.split()[1]
                        return version_str.strip()
            elif platform_str == "Windows":
                ret = subprocess.run(
                    [self.dfu_app, "info", f"-g{self.driver_guid}"],
                    **common_opts,
                )
                bcd_re = r"\d+\s+0x20B1\s+0x0016\s+0x(?P<bcd>\d{4})\s+"
                match = re.search(bcd_re, ret.stdout)
                if match:
                    match_dict = match.groupdict()
                    bcd_ver = match_dict["bcd"]
                    return f"{bcd_ver[:2]}.{bcd_ver[2:]}"

        pytest.fail(f"Failed to get device version after {timeout}s")

    def download(self, image_bin, dfuapp="custom"):
        my_env = os.environ.copy()
        if dfuapp == "dfu-util":
            lib_path = my_env.pop("DYLD_LIBRARY_PATH", None)   # The copy of libusb in tools 15.2.1 doesn't work with dfu-util. TODO Remove this when migrating to tools 15.3
            print(f"lib_path = {lib_path}")
            cmd = ["dfu-util", "-d", f"0x20b1:{hex(self.pid)}", "-D", image_bin, "-R"]
            check = False # dfu-util download despite succeeding returns retcode -5 (LIBUSB_ERROR_NOT_FOUND) when it tries
            # to reset the device after detaching post download (https://github.com/Stefan-Schmidt/dfu-util/blob/master/src/main.c#L1163)
        else:
            check = True
            platform_str = platform.system()
            if platform_str in ["Darwin", "Linux"]:
                cmd = [self.dfu_app, f"{hex(self.pid)}", "--download", image_bin]
            elif platform_str == "Windows":
                # Issue 122: need a delay before DFU download, otherwise dfucons can fail
                time.sleep(10)
                cmd = [self.dfu_app, "download", image_bin, f"-g{self.driver_guid}"]
            else:
                pytest.fail(f"Unsupported platform: {platform_str}")
        ret = subprocess.run(cmd, env=my_env, **common_opts)
        print(ret.stdout)
        if ret.returncode and check:
            pytest.fail(
                f"Download of image {image_bin} failed (error {ret.returncode})"
            )

    def upload(self, dfuapp="custom"):
        my_env = os.environ.copy()
        if dfuapp == "dfu-util":
            my_env.pop("DYLD_LIBRARY_PATH", None)   # The copy of libusb in tools 15.2.1 doesn't work with dfu-util. TODO Remove this when migrating to tools 15.3
            cmd = ["dfu-util", "-d", f"0x20b1:{hex(self.pid)}", "-U", self.upload_bin, "-R"]
            check = False # See comment in download()
        else:
            check = True
            platform_str = platform.system()
            if platform_str in ["Darwin", "Linux"]:
                cmd = [self.dfu_app, f"{hex(self.pid)}", "--upload", self.upload_bin]
            elif platform_str == "Windows":
                cmd = [self.dfu_app, "upload", self.upload_bin, f"-g{self.driver_guid}"]
            else:
                pytest.fail(f"Unsupported platform: {platform_str}")
        ret = subprocess.run(cmd, env=my_env, **common_opts)
        if ret.returncode and check:
            print(ret.stdout)
            pytest.fail(
                f"Upload image to {self.upload_bin} failed (error {ret.returncode})"
            )

    def revert_factory(self):
        platform_str = platform.system()
        if platform_str in ["Darwin", "Linux"]:
            cmd = [self.dfu_app, f"{hex(self.pid)}", "--revertfactory"]
        elif platform_str == "Windows":
            cmd = [self.dfu_app, "revertfactory", f"-g{self.driver_guid}"]
        else:
            pytest.fail(f"Unsupported platform: {platform_str}")
        ret = subprocess.run(cmd, **common_opts)
        if ret.returncode:
            print(ret.stdout)
            pytest.fail(f"Revert to factory failed (error {ret.returncode})")


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


def dfu_uncollect(pytestconfig, board, config, dfuapp):
    # XTAG not present
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        return True
    if platform.system() == "Windows" and dfuapp == "dfu-util":
        return True
    level = pytestconfig.getoption("level")
    if level == "smoke":
        # Just run on xk_316_mc at smoke level
        return board not in ["xk_316_mc", "xk_216_mc"]
    return False


@pytest.mark.uncollect_if(func=dfu_uncollect)
@pytest.mark.parametrize(["board", "config"], dfu_testcases)
@pytest.mark.parametrize("dfuapp", ["custom", "dfu-util"])
def test_dfu(pytestconfig, board, config, dfuapp):
    with DfuTester(pytestconfig, board, config) as dfu_test:
        # xflash the factory image for the initial version
        firmware = get_firmware_path(board, config)
        subprocess.run(
            ["xflash", "--adapter-id", dfu_test.xtag_id, "--factory", firmware],
            check=True,
        )
        initial_version = dfu_test.get_bcd_version()
        exp_version1 = "99.01"
        exp_version2 = "99.02"

        # perform the first upgrade
        dfu_bin1 = create_dfu_bin(board, "upgrade1")
        dfu_test.download(dfu_bin1, dfuapp=dfuapp)
        version = dfu_test.get_bcd_version()
        if version != exp_version1:
            pytest.fail(f"Unexpected version {version} after first upgrade")

        # perform the second upgrade
        dfu_bin2 = create_dfu_bin(board, "upgrade2")
        dfu_test.download(dfu_bin2, dfuapp=dfuapp)
        version = dfu_test.get_bcd_version()
        if version != exp_version2:
            pytest.fail(f"Unexpected version {version} after second upgrade")

        dfu_test.upload(dfuapp=dfuapp)
        version = dfu_test.get_bcd_version()
        if version != exp_version2:
            pytest.fail(f"Unexpected version {version} after reading upgrade image")

        dfu_test.revert_factory()
        version = dfu_test.get_bcd_version()
        if version != initial_version:
            pytest.fail(
                f"After factory reset, version {version} didn't match initial {initial_version}"
            )

        dfu_test.download(dfu_test.upload_bin, dfuapp=dfuapp)
        version = dfu_test.get_bcd_version()
        if version != exp_version2:
            pytest.fail(
                f"Unexpected version {version} after writing the image that was read"
            )

        # Finish by reverting back to the factory image again
        dfu_test.revert_factory()
        version = dfu_test.get_bcd_version()
        if version != initial_version:
            pytest.fail(
                f"Version {version} didn't match initial {initial_version} after final factory reset"
            )
