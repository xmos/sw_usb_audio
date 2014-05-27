XMOS XS1-U8 USB Audio
=====================

:maintainer: Ross Owen
:scope: General Use
:description: USB Audio application for XP-SKC-SU1 and XA-SK-AUDIO (1v1)
:keywords: USB, audio, U8  
:boards: XP-SKC-SU1, XA-SK-AUDIO (1v1)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

Key Features
............

The app_usb_aud_skc_su1 application is designed to run on the U8 Slice Kit Core Board (XP-SKC-SU1) in conjunction with an Audio Slice (XA-SK-AUDIO).  It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 4 channels analogue input and 4 channels analogue output (Via I2S to 2 x Stereo CODECs)

- S/PDIF output (via COAX connector)
  
- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Known Issues
............

Please note that this software is not compatible with version 1v0 of the Audio Slice board (XA-SK-AUDIO) due to a pin-out change between versions 1v0 and 1v1.

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


