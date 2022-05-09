XMOS xcore.ai USB Audio
=======================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE.ai eXplorer board
:keywords: USB, UAC
:boards: XK-EVK-XU316 (rev 2.0)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS xCORE.ai device.

Note, this project only functions on revision 2 of the XK-EVK-XU316 board. Early versions of the hardware require modifications to both the hardware and software to operate correctly. 


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


