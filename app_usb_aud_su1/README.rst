XMOS SU1 USB Audio
==================

:Latest release: 6.0.0alpha10
:Maintainer: Ross Owen
:scope: Example
:description: USB Audio application for XR-USB-AUDIO-S1
:keywords: USB, Audio, I2S, S/PDIF, SU1 
:boards: XP-SKC-SU1, XA-SK-AUDIO (1v0)

Please note, this application is provided as legacy support for the early prototype board XR-USB-AUDIO-S1.  This has now been superseded by the combination of boards XP-SKC-SU1 and XA-SK-AUDIO (Termed the XMOS USB Audio DJ Kit) and the application app_usb_aud_skc_su1.  It is advised that any evaluation and development ismoved away from this platform.   

Key Features
............

The app_usb_aud_su1 application is designed to run on the XR-USB-AUDIO-S1.  It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchorous operation

- 2 channels analogue input and 2 channels analogue output (Via I2S to 1 x Stereo CODEC)

- S/PDIF output (via COAX connector)
  
- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Overview
........

The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

CODEC configuration takes place via I2C.

Known Issues
............

- Buttons A and B currently have no functionality attached to them

See README in sw_usb_aud for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


