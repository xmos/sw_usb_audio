XMOS xcore.ai USB Audio
=======================

:scope: Example
:description: USB Audio application for xcore.ai MC Audio
:keywords: USB, UAC
:boards: XK-AUDIO-316-MC

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the
USB Audio Class Specification based on the xcore.ai device.

Key Features
............

The app_usb_aud_xk_316_mc application is designed to run on the xcore.ai Multichannel Audio Board.
It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 1.0/2.0 Compliant

- Fully Asynchronous operation

- 8 channels analogue input and 8 channels analogue output (Via I²S to 4 x Stereo DACs and 2 x Quad-channel ADCs)

- S/PDIF output (via COAX connector)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Known Issues
............

- None

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


