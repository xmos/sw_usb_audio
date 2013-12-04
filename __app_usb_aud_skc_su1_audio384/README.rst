XMOS XS1-U8 USB Audio
=====================

:Latest release: 6.0.0alpha10
:Maintainer: Ross Owen
:scope: Example
:description: USB Audio application for XP-SKC-SU1 and XA-SK-AUDIO384
:keywords: USB,  
:boards: XP-SKC-SU1, XA-SK-AUDIO384

Overview
........

The app_usb_aud_skc_su1_audio384 application is designed to run on the U8 Slice Kit Core Board (XP-SKC-SU1) in conjunction with a 384kHz Audio Slice (XA-SK-AUDIO384).  It uses the XMOS USB Audio framework to implement a high-speed USB Audio device compliant to version 2.0 of the USB Audio Class Specification.

The XA-SK-AUDIO384 board includes a configurable master-clock source which is configured by the application. The makefile generates binaries for various master-clock ratios.

Key Features
............

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue output (Via I2S to 1 x Stereo DAC)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192, 352.8, 384kHz

Known Issues
............

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


