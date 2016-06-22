XMOS xCORE-200 USB Audio
========================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE-200 MC Audio
:keywords: USB, UAC
:boards: XCORE-200 MC AUDIO (rev 2.0)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS U16 device.

Key Features
............

The app_usb_aud_xk_216_mc application is designed to run on the xCORE 200 MC Audio Board in. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 4 channels analogue input and 4 channels analogue output (Via I2S to 2 x Stereo CODECs)

- S/PDIF output (via COAX connector)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Known Issues
............

- On occasion with the build configuration 2i8o8xxxxx_tdm8_slave (or any configuration where the Cirrus CS5368 ADC is used as clock master and the Cirrus CS4364 DAC slaves to this clock) sample-rate changes can cause a channel swapping issue in the Cirrus DAC. This incompatibility is documented in Cirrus note AN302 (https://www.cirrus.com/en/pubs/appNote/AN302REV1.pdf) 

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


