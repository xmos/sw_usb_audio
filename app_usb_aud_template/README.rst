##############################
Template USB Audio application
##############################

:scope: Example
:description: Template USB Audio application
:keywords: USB, UAC
:boards:

*******
Summary
*******

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the
USB Audio Class Specification based on the xcore.ai device.

********
Features
********

The app_usb_aud_template application is a template application provided as a good starting point for
porting to custom hardware.

It uses the XMOS USB Audio framework to implement a USB Audio device with the following default
key features:

- USB Audio Class 1.0/2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input and 2 channels analogue output

- Support for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

************
Known Issues
************

- None

See README in sw_usb_audio for general issues.

*******
Support
*******

For all support issues please visit http://www.xmos.com/support


