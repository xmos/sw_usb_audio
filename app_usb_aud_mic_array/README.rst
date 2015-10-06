XMOS xCORE-200 USB Audio
========================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE-200 MC Audio
:keywords: USB,
:boards: XCORE-200 MC AUDIO (rev 2.0)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS U16 device.

Key Features
............

The app_usb_aud_x200 application is designed to run on the xCORE 200 MC Audio Board in. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 4 channels analogue input and 4 channels analogue output (Via I2S to 2 x Stereo CODECs)

- S/PDIF output (via COAX connector)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Known Issues
............

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


