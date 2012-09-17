XMOS SU1 USB Audio
==================

:Latest release: 6.0.0alpha10
:Maintainer: Ross Owen
:scope: Example
:description: USB Audio application for XP-SKC-SU1 and XA-SK-AUDIO (1v0)
:keywords: USB 
:boards: XP-SKC-SU1, XA-SK-AUDIO (1v0)


Key Features
............

The app_usb_aud_skc_su1 application is designed to run on the SU1 Slice Kit Core Board (XP-SKC-SU1) in conjunction with an Audio Slice (XA-SK_AUDIO).  It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchorous operation

- 4 channels analogue input and 4 channels analogue output (Via I2S to 2 x Stereo CODECs)

- S/PDIF output (via COAX connector)
  
- Supports for the following sample frequencies: 44.1, 48, 88.2, 176.4, 192kHz


Overview
........

The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.


Known Issues
............

See README in sw_usb_aud for general issues.


