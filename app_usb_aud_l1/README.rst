XMOS XS1-L1 USB Audio 2.0 Reference Design (app_usb_aud_l1)
...........................................................

:Latest release: 6.0.0alpha10
:Maintainer: Ross Owen

Key Features
============

The app_usb_aud_l1 application is designed to run on the XMOS USB Audio 2.0 references design board
(part number xr-usb-audio-2.0).  This application used the XMOS USB Audio framework. Key features 
of this application are as follows: 

- USB Audio Class 2.0 Compliant  

- Fully Asynchronous operation

- Stereo analogue input and output

- S/PDIF Output

- Supports the following sample frequencies: 44.1, 48, 88.2, 96, 176.4*, 192kHz

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

* S/PDIF Output at 176.4kHz not supported due to mclk requirements


Overview
========

The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

When connected via a full-speed hub the device falls back to operate at Audio 1.0 at full-speed.  A different PID is used to 
avoid Windows driver caching issues.

Additionally, build options are provided for Audio Class 1.0.  To remain compliant this causes the device to run at full-speed.

When running at full-speed sample-frequency restrictions are enforced to ensure fitting within the band-width restrictions of 
full-speed USB.

The firmware provides stereo input and output via I2S and stereo output via S/PDIF.  Build options are provided to enable/disable 
input and output functionality.


Known Issues
============

-  Buttons A and B currently have no functionality attached to them

-  CODEC (CS4270) auto-mute/soft-ramp feature can cause volume ramp at start of playback.  These features cannot be disabled on the reference board since CODEC is used in Hardware Mode (i.e. not configured using I2C)


Support
=======

For all support issues please visit http://www.xmos.com/support


