XMOS USB Audio 2.0 Reference Design README
..........................................

Please note, Alpha and Beta releases may not accurately reflect the final release and documentation may not be complete. These early releases are not suitable for a production context, and are provided for evaluation purposes only.

Welcome to version 6 of the XMOS USB Audio Software Framework.

Please see CHANGELOG.rst for detailed change listing.

For full software documentation please see the USB Audio Design Guide document.

This release is built and tested using version 14.3.3 of the XMOS tool set.  Build or functionality issues could be experienced with any other version.

This repository contains applications (or instances) of the XMOS USB Audio Reference Design framework.  These applications
typically relate to a specific board.

Please refer to individual README files in these apps for more detailed information.

Each application contains a "core" folder, this folder contains items that are required to use and run the USB Audio application framework.  
Mandatory files per application include: 

- An XN file describing the board including required port defines. The XN file is referenced in the application makefile.
- customdefines.h header file containing configuration items such as channel count, strings etc.

Each application also contains an "extensions" folder which includes board specific extensions such as CODEC configuration etc.

Additionally some options are contained in Makefiles for building multiple configurations of an application. For example 
app_usb_aud_l1 builds a MIDI and S/PDIF configurations.  See the USB Audio Software Design Guide for full details.

Key Framework Features
======================

Key features of the various applications in this repository are as follow.  Please refer to the application README for application specific feature set.

- USB Audio Class 1.0/2.0 Compliant 

- Fully Asynchronous operation

- Support for the following sample frequencies: 8, 11.025, 12, 16, 32, 44.1, 48, 88.2, 96, 176.4, 192, 352.8, 384kHz

- Input/output channel and individual volume/mute controls supported

- Support for dynamically selectable output audio formats (e.g. resolution)

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

- S/PDIF output

- S/PDIF input

- ADAT output

- ADAT input

- MIDI input/output (Compliant to USB Class Specification for MIDI devices)

- DSD output (Native and DoP mode) at DSD64 and DSD128 rates

- Mixer with flexible routing

- Simple playback controls via Human Interface Device (HID)

- Support for operation with Apple devices (requires software module sc_mfi for MFI licensees only - please contact XMOS) 

Note, not all features may be supported at all sample frequencies, simultaneously or on all devices.  Some features also require specific host driver support.

Known Issues
============

General known issues with this release are listed below.  For board/application specific known issues please see README in relevant app directory

- Quad-SPI DFU will corrupt the factory image with tools version less than 14.0.4 due to an issue with libquadflash 

- (#14762) When in DSD mode with S/PDIF output enabled, DSD samples are transmitted over S/PDIF if the DSD and S/PDIF channels are shared, this may or may not be desired

- (#14173) I2S input is completely disabled when DSD output is active - any input stream to the host will contain 0 samples

- (#14780) Operating the design at a sample rate of less than or equal to the SOF rate (i.e. 8kHz at HS, 1kHz at FS) may expose a corner case relating to 0 length packet handling in both the driver and device and should be considered un-supported at this time.

- (#14883) Before DoP mode is detected a small number of DSD samples will be played out as PCM via I2S

- (#14887) Volume control settings currently affect samples in both DSD and PCM modes. This results in invalid DSD output if volume control not set to 0

-  Windows XP volume control very sensitive.  The Audio 1.0 driver built into Windows XP (usbaudio.sys) does not properly support master volume AND channel volume controls, leading to a very sensitive control.  Descriptors can be easily modified to disable master volume control if required (one byte - bmaControls(0) in Feature Unit descriptors)

-  88.2kHz and 176.4kHz sample frequencies are not exposed in Windows control panels.  These are known OS restrictions.

Host System Requirements
========================

- OS X/macOS version 10.6 or later

- Windows XP, Vista, 7, 8 or 10 with Thesycon Audio Class 2.0 driver for Windows (Tested against version 4.11.0). Please contact XMOS for details.
 
- Windows XP, Vista, 7, 8 or 10 with built-in USB Audio Class 1.0 driver.

In Field Firmware Upgrade
=========================

The firmware provides a Device Firmware Upgrade (DFU) interface compliant to the USB DFU Device Class.  An example host application is provided for OSX.  See README in example application for usage.  The Thesycon USB Audio Class 2.0 driver for Windows provides DFU functionality and includes an example application.

Support
=======

For all support issues please visit http://www.xmos.com/support
