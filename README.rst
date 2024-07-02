XMOS USB Audio 2.0 Reference Design README
##########################################

:Version: 8.1.0
:Vendor: XMOS

Please note, Alpha and Beta releases may not accurately reflect the final release and documentation may not be complete. These early releases are not suitable for a production context, and are provided for evaluation purposes only. See 'Release Quality & QA'.

Please see CHANGELOG.rst for detailed change listing.

For full software documentation please see the USB Audio User Guide document.

This release is built and tested using version 15.2.1 of the XMOS tool set.  Build or functionality issues could be experienced with any other version.

This repository contains applications (or instances) of the XMOS USB Audio Reference Design framework.  These applications
typically relate to a specific hardware platform.  This repository contains the following:

+--------------------------+--------------------------+------------------------------------------------------------+
|    App Name              |     Relevant Board(s)    | Description                                                |
+==========================+==========================+============================================================+
| app_usb_aud_xk_216_mc    | xk-audio-216-mc          | xcore-200 Multi-channel Audio Board                        |
+--------------------------+--------------------------+------------------------------------------------------------+
| app_usb_aud_xk_316_mc    | xk-audio-316-mc          | xcore.ai Multi-channel Audio Board                         |
+--------------------------+--------------------------+------------------------------------------------------------+
| app_usb_aud_xk_evk_xu316 | xk-evk-xu316             | xcore.ai Explorer Board                                    |
+--------------------------+--------------------------+------------------------------------------------------------+

Please refer to individual README files in these apps for more detailed information.

Each application contains a "core" folder, this folder contains items that are required to use and run the USB Audio application framework.
Mandatory files per application include:

- An XN file describing the board including required port defines. The XN file is referenced in the application makefile.
- xua_conf.h header file containing configuration items such as channel count, strings etc.

Each application also contains an "extensions" folder which includes board specific extensions such as CODEC configuration etc.

Additionally some options are contained in Makefiles for building multiple configurations of an application. For example an application may provide configurations with and without MIDI enabled.  See the USB Audio Software User Guide for full details.

Key Features
============

Key features of the various applications in this repository are listed below.  Please refer to the application README the specific feature set supported by that application.

- USB Audio Class 1.0/2.0 Compliant

- Fully Asynchronous operation (Synchronous mode as an option)

- Support for the following sample frequencies: 8, 11.025, 12, 16, 32, 44.1, 48, 88.2, 96, 176.4, 192, 352.8, 384kHz

- Input/output channel and individual volume/mute controls supported

- Support for dynamically selectable output audio formats (e.g. resolution)

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

- S/PDIF output

- S/PDIF input

- ADAT output

- ADAT input

- MIDI input/output (Compliant to USB Class Specification for MIDI devices)

- DSD output ("Native" and DoP mode) at DSD64 and DSD128 rates

- Mixer with flexible routing

- Simple playback controls via Human Interface Device (HID)

Note, not all features may be supported at all sample frequencies, simultaneously or on all devices.  Some features also require specific host driver support.

Release Quality & QA
====================

+---------------------------+--------------------------+
| Feature                   | Quality                  |
+===========================+==========================+
| Audio Class 1.0 Streaming | Release                  |
+---------------------------+--------------------------+
| Audio Class 2.0 Streaming | Release                  |
+---------------------------+--------------------------+
| I2S Master                | Release                  |
+---------------------------+--------------------------+
| I2S Slave                 | Release                  |
+---------------------------+--------------------------+
| TDM Master                | Release                  |
+---------------------------+--------------------------+
| TDM Slave                 | Release                  |
+---------------------------+--------------------------+
| S/PDIF Receive            | Release                  |
+---------------------------+--------------------------+
| S/PDIF Transmit           | Release                  |
+---------------------------+--------------------------+
| ADAT Receive              | Release                  |
+---------------------------+--------------------------+
| ADAT Transmit             | Release                  |
+---------------------------+--------------------------+
| MIDI I/O                  | Release                  |
+---------------------------+--------------------------+
| DSD Playback              | Beta                     |
+---------------------------+--------------------------+
| Mixer                     | Release                  |
+---------------------------+--------------------------+
| HID Controls              | Beta                     |
+---------------------------+--------------------------+

Known Issues
============

General known issues with this release are listed below.  For board/application specific known issues please see README in relevant app directory

- (xmos/sw_usb_audio#54) When DFU flash access fails the xcore sends NAKs to the USB host forever, rather than a STALL

- (xmos/sw_usb_audio#97) Documentation missing for XK-EVK-316

- (xmos/sw_usb_audio#99) Input via TDM master unreliable due to low-level timing issues (xcore-200 only)

- (xmos/sw_usb_audio#120) Playback glitches experienced at 44.1/48kHz when using ASIO4ALL (v2.15) with built-in windows drivers. USB bus traces prove that these originate from the host driver.

- (#14762) When in DSD mode with S/PDIF output enabled, DSD samples are transmitted over S/PDIF if the DSD and S/PDIF channels are shared, this may or may not be desired

- (#14173) I2S input is completely disabled when DSD output is active - any input stream to the host will contain 0 samples

- (#14780) Operating the design at a sample rate of less than or equal to the SOF rate (i.e. 8kHz at HS, 1kHz at FS) may expose a corner case relating to 0 length packet handling in both the driver and device and should be considered unsupported at this time.

- (#14883) Before DoP mode is detected a small number of DSD samples will be played out as PCM via I2S

- (#14887) Volume control settings currently affect samples in both DSD and PCM modes. This results in invalid DSD output if volume control not set to 0

-  Windows XP volume control very sensitive.  The Audio 1.0 driver built into Windows XP (usbaudio.sys) does not properly support master volume AND channel volume controls, leading to a very sensitive control.  Descriptors can be easily modified to disable master volume control if required (one byte - bmaControls(0) in Feature Unit descriptors)

-  88.2kHz and 176.4kHz sample frequencies are not exposed in Windows control panels.  These are known OS restrictions in Windows 7 and earlier.

-  Compatibility issues exist with the Microsoft built in UAC1.0 driver (usbaudio.sys) and Intel Smart Sound Technology (SST) can result in audible distortions. This can be worked around by disabling the SST driver.

Host System Requirements
========================

USB Audio Class 1.0
-------------------

- macOS version 10.6 or later
- Windows XP, Vista, 7, 8, 10, or 11 with built-in USB Audio Class 1.0 driver.

USB Audio Class 2.0
-------------------

- macOS version 10.6 or later
- Windows 10 or 11 with built-in USB Audio Class 2.0 driver.
- Windows 10 or 11 using built-in or Thesycon Audio Class 2.0 driver for Windows (Tested against version 5.5)

In Field Firmware Upgrade
=========================

The firmware provides a Device Firmware Upgrade (DFU) interface compliant to the USB DFU Device Class.  An example host application is provided for OSX.  See README in example application for usage.  The Thesycon USB Audio Class 2.0 driver for Windows provides DFU functionality and includes an example application.

Required Software (dependencies)
================================

  * lib_sw_pll (www.github.com/xmos/lib_sw_pll)
  * lib_xua (www.github.com/xmos/lib_xua)
  * lib_adat (www.github.com/xmos/lib_adat)
  * lib_locks (www.github.com/xmos/lib_locks)
  * lib_logging (www.github.com/xmos/lib_logging)
  * lib_mic_array (www.github.com/xmos/lib_mic_array)
  * lib_xassert (www.github.com/xmos/lib_xassert)
  * lib_dsp (www.github.com/xmos/lib_dsp)
  * lib_spdif (www.github.com/xmos/lib_spdif)
  * lib_xud (www.github.com/xmos/lib_xud)
  * lib_i2c (www.github.com/xmos/lib_i2c)
  * lib_i2s (www.github.com/xmos/lib_i2s)

Documentation
=============

You can find the documentation for this software in the /doc directory of the package.

Support
=======

This package is supported by XMOS Ltd. Issues can be raised against the software at: http://www.xmos.com/support
