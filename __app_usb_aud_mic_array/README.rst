XMOS xCORE-200 Mic Array
========================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE Microphone Array board
:keywords: USB, Mic, PDM, UAC
:boards: XCORE-200 Microphone Array Ref Design (1v0)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS U16 device.

Key Features
............

The app_usb_aud_mic_array application is designed to run on the xCORE Microphone Array board. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 7 channels input from 7 PDM mics (including PDM to PCM conversion)
  
- 2 channels analogue output (Via I2S to a stereo DAC)

Known Issues
............

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


