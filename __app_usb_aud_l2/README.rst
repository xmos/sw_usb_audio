XMOS XS1-L2 USB Audio 2.0 Reference Design (app_usb_aud_l2)
===========================================================

:maintainer: Ross Owen, XMOS Limited
:scope: General Use
:description: USB Audio for L2 USB Audio
:keywords: USB, Audio, L2
:boards: XR-USB-AUDIO-2.0-MC

Overview
........

The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

The firmware provides multi-channel input and output via I2S and stereo output via S/PDIF.  Build options are provided to enable/disable 
input and output functionality.

Key Features
............

The app_usb_aud_l2 application is designed to run on the XMOS USB Audio 2.0 References Design board (part number xr-usb-audio-2.0-mc).  This application uses the XMOS USB Audio framework. 

Key features of this application are as follows: 

- USB Audio Class 2.0 Compliant  

- Fully Asynchronous operation

- Multi-channel analogue input and output

- S/PDIF Output

- Supports the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

Please note, not all features may be supported at all sample frequencies

Known Issues
............

See README in sw_usb_audio for general issues.

- Increased noise floor can be experianced on analogue channels during operation when XTAG2 is connected.  This noise is due to contention (#8611)

Support
.......

For all support issues please visit http://www.xmos.com/support


