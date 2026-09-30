##############################
XMS0028 USB Audio application
##############################

:scope: Example
:description: XMS0028 USB Audio application
:keywords: USB, UAC
:boards: XMS0028

*******
Summary
*******

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the
USB Audio Class Specification based on the XCORE.AI device.

********
Features
********

The app_usb_aud_xms0028 application targets the XMS0028 XU316 board. It uses
``lib_board_support`` to configure the TLV320AIC3204 stereo codec, I2C master, shared
CODEC-reset/LED GPIO port and fixed master clock. Capture uses the stereo line input.

It uses the XMOS USB Audio framework to implement a USB Audio device with the following default
key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input and 2 channels analogue output

- Support for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

************
Known issues
************

- None

See README in sw_usb_audio for general issues.

*******
Support
*******

For all support issues please visit http://www.xmos.com/support

