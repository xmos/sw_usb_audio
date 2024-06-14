# Copyright (c) 2020-2022, XMOS Ltd, All rights reserved
from pathlib import Path
import pytest
import re
import subprocess

from hardware_test_tools.UaDfuApp import UaDfuApp
from conftest import get_firmware_path, AppUsbAudDut, get_xtag_dut


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


def xtc_version():
    version_re = r"XTC version: (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    ret = subprocess.run(["xcc", "--version"], capture_output=True, text=True)
    match = re.search(version_re, ret.stdout)
    if not match:
        pytest.fail(f"Unable to get XTC Tools version: stdout={ret.stdout}")
    return match.groupdict()


# Test cases are defined by a tuple of (board, initial config to xflash)
dfu_testcases = [
    ("xk_216_mc", "2AMi10o10xssxxx"),
    ("xk_316_mc", "2AMi10o10xssxxx"),
    ("xk_evk_xu316", "2AMi2o2xxxxxx"),
]


def dfu_uncollect(pytestconfig, board, config):
    # XTAG not present
    xtag_id = get_xtag_dut(pytestconfig, board)
    if not xtag_id:
        return True
    level = pytestconfig.getoption("level")
    if level == "smoke":
        # Just run on xk_316_mc at smoke level
        return board not in ["xk_316_mc"]
    return False


@pytest.mark.uncollect_if(func=dfu_uncollect)
@pytest.mark.parametrize(["board", "config"], dfu_testcases)
def test_dfu(pytestconfig, board, config):
    adapter_dut = get_xtag_dut(pytestconfig, board)

    with AppUsbAudDut(adapter_dut, board, config, xflash=True) as dut:
        dfu_test = UaDfuApp(dut.driver_guid, dut.features["pid"])

        initial_version = dfu_test.get_bcd_version()
        exp_version1 = "99.01"
        exp_version2 = "99.02"

        # perform the first upgrade
        dfu_bin1 = create_dfu_bin(board, "upgrade1")
        dfu_test.download(dfu_bin1)
        version = dfu_test.get_bcd_version()
        if version != exp_version1:
            pytest.fail(f"Unexpected version {version} after first upgrade")

        # perform the second upgrade
        dfu_bin2 = create_dfu_bin(board, "upgrade2")
        dfu_test.download(dfu_bin2)
        version = dfu_test.get_bcd_version()
        if version != exp_version2:
            pytest.fail(f"Unexpected version {version} after second upgrade")

        upload_file = Path(__file__).parent / "test_dfu_upload.bin"
        dfu_test.upload(upload_file)
        version = dfu_test.get_bcd_version()
        if version != exp_version2:
            pytest.fail(f"Unexpected version {version} after reading upgrade image")

        dfu_test.revert_factory()
        version = dfu_test.get_bcd_version()
        if version != initial_version:
            pytest.fail(
                f"After factory reset, version {version} didn't match initial {initial_version}"
            )

        dfu_test.download(upload_file)
        upload_file.unlink()
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
