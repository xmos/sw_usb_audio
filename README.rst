XMOS USB Audio 2.0 Reference Designs (sw_usb_audio)
===================================================

This repo contains applications (or instances) of the XMOS USB Audio Reference Design framework.  These applications
typically relate to a specific board.

Each application contains a "core" folder, this folder contains items that are required to use and runthe USB audio 
application framework on a board.

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


Support
=======

For all support issues please visit http://www.xmos.com/support
