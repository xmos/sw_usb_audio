XMOS XK-USB-AUDIO-U8-2C USB Audio (app_usb_aud_xk_u8_2c)
========================================================

:maintainer: Ross Owen
:scope: General Use
:description: USB Audio for XK-USB-AUDIO-U8-2C board
:keywords: USB, Audio, MFA
:boards: XK-USB-AUDIO-U8-2C (2v0)

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

Key Features
............

The app_usb_aud_xk_u8_2c application is designed to run on the XMOS Multi-Function Audio (MFA) Board (XR-USB-AUDIO-U8-2C) version 2.0.  This should be used in conjunction with a valid USB Slice including valid USB Device functionality (e.g. a USB B connector).  The application uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input (Via I2S from 1 x stereo ADC)

- 2 channels analogue output (Via I2S to 1 x stereo DAC), configured via I2C

- Stereo DSD output (Both Native and DoP)

- S/PDIF output (via COAX connector)

- MIDI input and output

- Support for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- Two push-buttons implementing HID compliant controls such as play/pause, skip, back etc.

- One two-position switch for software use

- Two LED's for software use

- Support for operation with Apple devices (MFI licensees only - please contact XMOS)

Note, DSD requires driver and/or player support.

Known Issues
............

See README in sw_usb_audio for general issues.

- (#14653) DSD over PCM (DoP) 128 mode requires an effective PCM rate of 352.8kHz. Since the DAC is not rated to this speed in PCM mode this is not enabled by default.  It can be enabled by modifying the MAX_FREQ define.

- (#14996) Exception during enumeration if xCORE is booted from flash when using tools version 13. This is resolved in tools version 13.0.1 and later.

Support
.......

For all support issues please visit http://www.xmos.com/support
