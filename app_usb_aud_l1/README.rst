XMOS USB Audio 2.0 Reference Design (XS1-L1)
............................................

Key Features
============

- USB Audio Class 2.0 Compliant  

- Fully Asynchronous operation

- Stereo analogue input and output

- S/PDIF Output

- Supports the following sample frequencies: 44.1, 48, 88.2, 96, 176.4*, 192kHz

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

* S/PDIF Output at 176.4kHz not supported due to mclk requirements


Firmware Detail
===============

Overview
--------
The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

When connected via a full-speed hub the device falls back to operate at Audio 1.0 at full-speed.  A different PID is used to 
avoid Windows driver caching issues.

Additionally, build options are provided for Audio Class 1.0.  To remain compliant this causes the device to run at full-speed.

When running at full-speed sample-frequency restrictions are enforced to ensure fitting within the band-width restrictions of 
full-speed USB.

The firmware provides stereo input and output via I2S and stereo output via S/PDIF.  Build options are provided to enable/disable 
input and output functionality.

In Field Firmware Upgrade
-------------------------
The firmware provides a DFU interface compliant to the USB DFU Device Class.  An example host application is provided for OSX.  See README in example application for usage.  The Thesycon USB Audio Class 2.0 driver for Windows provides DFU functionality and includes an example application.


Known Issues
============

-  Buttons A and B currently have no functionality attached to them

-  CODEC (CS4270) auto-mute/soft-ramp feature can cause volume ramp at start of playback.  These features cannot be disabled on the reference board since CODEC is used in Hardware Mode (i.e. not configured using I2C)


Host System Requirements
========================

- Mac OSX version 10.6 or later

- Windows XP, Vista or 7 with Thesycon Audio Class 2.0 driver for Windows (contact XMOS for details)
  

Support
=======

For all support issues please visit http://www.xmos.com/support


