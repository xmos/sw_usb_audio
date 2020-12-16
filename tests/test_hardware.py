import io
import pytest
import sh
import time
import xtagctl

from usb_audio_test_tools import *

from hardware_configs import configs


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_input_8ch.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i10o10xxxxxx")], indirect=True)
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_input(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        xtagctl.reset_adapter(adapter_harness)
        time.sleep(2)  # Wait for adapters to enumerate
        # xrun the harness
        harness_firmware = get_firmware_path_harness("xcore200_mc")
        sh.xrun("--adapter-id", adapter_harness, harness_firmware)
        # xflash the firmware
        firmware = build
        sh.xrun("--adapter-id", adapter_dut, firmware)
        # Wait for device to enumerate
        time.sleep(10)
        # Run xsig
        xsig_duration = (duration_ms / 1000) + 5
        xsig_output = run_audio_command(
            xsig_duration, xsig, fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config
        )
        xsig_lines = xsig_output.split("\n")
        # Check output
        expected_freqs = [(i + 1) * 1000 for i in range(num_chans)]
        assert check_analyzer_output(xsig_lines, expected_freqs)


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration", [10])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_output.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i2o2xxxxxd")], indirect=True)
@pytest.mark.parametrize("audio", [("two_tones_dop.flac",)], indirect=True)
@pytest.mark.parametrize("num_chans", [2])
def test_dsd_over_pcm_output(xsig, fs, duration, xsig_config, build, audio, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        print(f"Adapter DUT: {adapter_dut}, Adapter harness: {adapter_harness}")
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        xtagctl.reset_adapter(adapter_harness)
        time.sleep(2)  # Wait for adapters to enumerate
        # xrun the dut
        firmware = build
        sh.xrun("--adapter-id", adapter_dut, firmware)
        # xrun --xscope the harness
        harness_firmware = get_firmware_path_harness("xcore200_mc")
        xscope_out = io.StringIO()
        harness_xrun = sh.xrun(
            "--adapter-id",
            adapter_harness,
            "--xscope",
            harness_firmware,
            _out=xscope_out,
            _err_to_out=True,
            _bg=True,
            _bg_exc=False,
        )
        # Wait for device(s) to enumerate
        time.sleep(10)
        # Run ffmpeg for duration + 2 seconds
        card_num, dev_num = find_aplay_device("XMOS xCORE-200 MC")
        # fmt: off
        ffmpeg_cmd = sh.ffmpeg(
            "-i", audio[0],
            "-r", "176400",
            "-c", "pcm_s32le",
            "-t", duration + 2,
            "-f", "alsa", f"hw:{card_num},{dev_num}",
            _bg=True,
        )
        # fmt: on
        time.sleep(duration)
        # Get analyser output
        try:
            harness_xrun.kill_group()
            harness_xrun.wait()
        except sh.SignalException:
            # Killed
            pass
        xscope_str = xscope_out.getvalue()
        xscope_lines = xscope_str.split("\n")
        print("XSCOPE STRING:")
        print(xscope_str)
        # Wait for xsig to exit (timeout after 5 seconds)
        ffmpeg_cmd.wait(timeout=5)

        expected_freqs = [((i + 1) * 1000) + 500 for i in range(num_chans)]
        # We expect a single glitch at the start of the stream with DSD over PCM
        assert check_analyzer_output(xscope_lines, expected_freqs, glitch_tolerance=1)


@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_analogue_output.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i10o10xxxxxx")], indirect=True)
@pytest.mark.parametrize("num_chans", [8])
def test_analogue_output(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        print(f"Adapter DUT: {adapter_dut}, Adapter harness: {adapter_harness}")
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        xtagctl.reset_adapter(adapter_harness)
        time.sleep(2)  # Wait for adapters to enumerate
        # xrun the dut
        firmware = build
        sh.xrun("--adapter-id", adapter_dut, firmware)
        # xrun --xscope the harness
        harness_firmware = get_firmware_path_harness("xcore200_mc")
        xscope_out = io.StringIO()
        harness_xrun = sh.xrun(
            "--adapter-id",
            adapter_harness,
            "--xscope",
            harness_firmware,
            _out=xscope_out,
            _err_to_out=True,
            _bg=True,
            _bg_exc=False,
        )
        # Wait for device(s) to enumerate
        time.sleep(10)
        # Run xsig for duration_ms + 2 seconds
        xsig_cmd = sh.Command(xsig)(
            fs, duration_ms + 2000, XSIG_CONFIG_ROOT / xsig_config, _bg=True
        )
        time.sleep(duration_ms / 1000)
        # Get analyser output
        try:
            harness_xrun.kill_group()
            harness_xrun.wait()
        except sh.SignalException:
            # Killed
            pass
        xscope_str = xscope_out.getvalue()
        xscope_lines = xscope_str.split("\n")
        print("XSCOPE STRING:")
        print(xscope_str)
        # Wait for xsig to exit (timeout after 5 seconds)
        xsig_cmd.wait(timeout=5)

        expected_freqs = [((i + 1) * 1000) + 500 for i in range(num_chans)]
        assert check_analyzer_output(xscope_lines, expected_freqs)


@pytest.mark.skip(reason="SPDIF test is WIP")
@pytest.mark.parametrize("fs", [48000])
@pytest.mark.parametrize("duration_ms", [10000])
@pytest.mark.parametrize("xsig_config", ["mc_digital_input_8ch.json"])
@pytest.mark.parametrize("build", [("xk_216_mc", "2i16o16xxxaax")], indirect=True)
@pytest.mark.parametrize("num_chans", [10])
def test_spdif_input(xsig, fs, duration_ms, xsig_config, build, num_chans):
    if build is None:
        pytest.skip("Build not present")
    with xtagctl.acquire("usb_audio_mc_xs2_dut", "usb_audio_mc_xs2_harness") as (
        adapter_dut,
        adapter_harness,
    ):
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        xtagctl.reset_adapter(adapter_harness)
        time.sleep(2)  # Wait for adapters to enumerate
        # xrun the harness
        harness_firmware = get_firmware_path_harness("xcore200_mc")
        sh.xrun("--adapter-id", adapter_harness, harness_firmware)
        # xflash the firmware
        firmware = build
        sh.xrun("--adapter-id", adapter_dut, firmware)
        # Wait for device to enumerate
        time.sleep(10)
        # Set the clock source to SPDIF
        card_num, dev_num = find_aplay_device("xCORE USB Audio")
        set_clock_source_alsa(card_num, "SPDIF")
        # Run xsig
        xsig_output = sh.Command(xsig)(fs, duration_ms, XSIG_CONFIG_ROOT / xsig_config)
        xsig_lines = xsig_output.split("\n")
        # Check output
        # expected_freqs = [(i+1) * 1000 for i in range(num_chans)]
        # assert check_analyzer_output(xsig_lines, expected_freqs)


@pytest.mark.parametrize(
    "build_with_dfu_test", [("xk_216_mc", "2i10o10xxxxxx")], indirect=True
)
def test_dfu(xmosdfu, build_with_dfu_test):
    if build_with_dfu_test is None:
        pytest.skip("Build not present")
    with xtagctl.acquire("usb_audio_mc_xs2_dut") as adapter_dut:
        # Reset both xtags
        xtagctl.reset_adapter(adapter_dut)
        time.sleep(2)  # Wait for adapters to enumerate
        # xflash the firmware
        firmware, dfu_bin = build_with_dfu_test
        sh.xflash("--adapter-id", adapter_dut, "--no-compression", firmware)
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


# if __name__ == "__main__":
#    test_analogue_output(
#        Path("./xsig").resolve(),
#        48000,
#        10000,
#        "mc_analogue_output.json",
#        ("xk_216_mc", "2i8o8xxxxx_tdm8"),
#        8,
#    )
