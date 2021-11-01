XMOS xcore.ai USB Audio
=======================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE.ai eXplorer board
:keywords: USB, UAC
:boards: xCORE.ai eXplorer (rev 1.x)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS xCORE.ai device.

Note, for correct operation external jumper cables must be attached between the following pins:

- MCLK to X0D11 (J14) (Version 1v0 hardware only)

Key Features
............

The app_usb_aud_xk_evk_xu316 application is designed to run on the xCORE.ai eXplorer board. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input and 2 channels analogue output (Via I2S to 1 x Stereo CODECs)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

Known Issues
............

- None.

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


