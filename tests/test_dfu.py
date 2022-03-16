# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
import os
from pathlib import Path
import platform
import pytest
import sh
import stat
import time
import requests
import xtagctl
import zipfile


XMOS_ROOT = Path(os.environ["XMOS_ROOT"])
XMOSDFU_LINUX_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/linux/xmosdfu"
XMOSDFU_MACOS_URL = "http://intranet.xmos.local/projects/usb_audio_regression_files/xmosdfu/macos/xmosdfu.zip"
XMOSDFU_PATH = Path(__file__).parent / "tools" / "xmosdfu"


def get_bcd_version(vid: int, pid: int) -> str:
    """Gets the BCD Device version number for a connected USB device with the
    specified VID and PID

    TODO: Windows support
    """

    if platform.system() == "Darwin":
        prof_out = sh.system_profiler.SPUSBDataType()
        prof_lines = prof_out.split("\n")
        xcore_lines = []
        current_pid = None
        current_vid = None
        for i, line in enumerate(prof_lines):
            if line.strip().startswith("Product ID:"):
                current_pid = int(line.split()[2], 16)
            if line.strip().startswith("Vendor ID:"):
                current_vid = int(line.split()[2], 16)
            if line.strip().startswith("Version"):
                if current_pid == pid and current_vid == vid:
                    return line.split()[1].strip()

        raise Exception(f"BCD Device not found: \n{prof_out}")
    elif platform.system() == "Linux":
        lsusb_out = sh.lsusb("-v", "-d", f"{hex(vid)}:{hex(pid)}")

        for line in lsusb_out.split("\n"):
            if line.strip().startswith("bcdDevice"):
                version_str = line.split()[1]
                return version_str.strip()

        raise Exception(f"BCD Device not found: \n{lsusb_out}")


def get_firmware_path(board, config):
    """ Gets the path to the firmware binary """

    firmware_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.xe"
    )
    return firmware_path


def get_dfu_bin_path(board, config):
    """ Gets the path to the DFU binary """

    dfu_bin_path = (
        XMOS_ROOT
        / "sw_usb_audio"
        / f"app_usb_aud_{board}"
        / "bin"
        / f"{config}"
        / f"app_usb_aud_{board}_{config}.bin"
    )
    return dfu_bin_path


@pytest.fixture
def xmosdfu():
    """Gets xmosdfu from projects network drive """

    XMOSDFU_PATH.parent.mkdir(parents=True, exist_ok=True)

    if platform.system() == "Darwin":
        r = requests.get(XMOSDFU_MACOS_URL)
        zip_path = XMOSDFU_PATH.parent / "xmosdfu.zip"
        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Unzip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(XMOSDFU_PATH.parent)

        XMOSDFU_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    elif platform.system() == "Linux":

        r = requests.get(XMOSDFU_LINUX_URL)
        with open(XMOSDFU_PATH, "wb") as f:
            f.write(r.content)

        XMOSDFU_PATH.chmod(stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    return XMOSDFU_PATH


def create_dfu_bin(board, config):
    """ Calls xflash on an existing firmware binary to create a DFU binary """

    firmware_path = get_firmware_path(board, config)
    dfu_bin_path = get_dfu_bin_path(board, config)
    sh.xflash(
        "--factory-version",
        "15.1",
        "--upgrade",
        "1",
        firmware_path,
        "-o",
        dfu_bin_path,
    )
    return dfu_bin_path


@pytest.mark.smoke
@pytest.mark.nightly
@pytest.mark.weekend
@pytest.mark.parametrize("board", ["xk_216_mc"])
def test_dfu(xmosdfu, board):
    with xtagctl.acquire("usb_audio_mc_xs2_dut") as adapter_dut:
        # xflash the firmware
        firmware = get_firmware_path(board, 'upgrade1')
        dfu_bin = create_dfu_bin(board, 'upgrade2')
        sh.xflash("--adapter-id", adapter_dut, firmware)
        # Wait for device to enumerate
        time.sleep(10)
        # Run DFU test procedure
        initial_version = get_bcd_version(0x20B1, 0x8)
        # Download the new firmware
        try:
            sh.Command(xmosdfu)("0x8", "--download", dfu_bin)
        except sh.ErrorReturnCode as e:
            print(e.stdout)
            raise Exception()
        time.sleep(3)
        # Check version
        upgrade_version = get_bcd_version(0x20B1, 0x8)
        # Revert to factory
        sh.Command(xmosdfu)("0x8", "--revertfactory")
        time.sleep(3)
        # Check version
        reverted_version = get_bcd_version(0x20B1, 0x8)

        assert initial_version == reverted_version
        assert upgrade_version != initial_version
