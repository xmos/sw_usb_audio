XMOS USB Audio 2.0 Reference Designs (sw_usb_audio)
...................................................

This repo contains applications (or instances) of the XMOS USB Audio Reference Design framework.  These applications
typically relate to a specific board.

Each application contains a "core" folder, this folder contains items that are required to use and run the USB audio 
application framework.  Mandatory files per application include: 

- An XN file describing the board (ports map etc). The filename referenced in the application makefile.
- customdefines.h header file containing configuration items such as channel count, strings etc.
- ports.h header file containing other ports that the application uses in addition to the required ports.

Each application also contains an "extensions" folder which includes board specific extensions such as CODEC 
configuration etc.

Additionally some options are contained in Makefiles for building multiple configurations of an application.


Key Framework Features
======================

Key features of the various applications in this repo as as follow.  Refer to the application README for application 
specific feature set.

- USB Audio Class 1.0/2.0 Compliant 

- Fully Asynchronous operation

- Support for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- Input/output master/channel volume/mute controls supported

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

- S/PDIF Output

- S/PDIF Input

- ADAT Input

- MIDI input/output (Compliant to USB Class Specification for MIDI devices)

- Mixer with flexible routing

Note, not all features may be supported at all sample frequencies, chips etc.


Known Issues
============

General known issues are as follows.  For board/application specific known issues please see README in relevant app.

-  Windows XP volume control very sensitive.  The Audio 1.0 driver built into Windows XP (usbaudio.sys) does not properly support master volume AND channel volume controls, leading to a very sensitive control.  Descriptors can be easily modified to disable master volume control if required (one byte - bmaControls(0) in Feature Unit descriptors)

-  88.2kHz and 176.4kHz sample frequencies are not exposed in Windows control panels.  This is due to known OS restrictions.


Host System Requirements
========================

- Mac OSX version 10.6 or later

- Windows XP, Vista or 7 with Thesycon Audio Class 2.0 driver for Windows (contact XMOS for details)


In Field Firmware Upgrade
=========================

The firmware provides a DFU interface compliant to the USB DFU Device Class.  An example host application is provided for OSX.  See README in example application for usage.  The Thesycon USB Audio Class 2.0 driver for Windows provides DFU functionality and includes an example application.


Support
=======

For all support issues please visit http://www.xmos.com/support
