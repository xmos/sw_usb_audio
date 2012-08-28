XMOS USB Audio 2.0 Reference Design (XS1-L1)
............................................

Key Features
============

- USB Audio Class 2.0 Compliant  

- Fully Asynchronous operation

- Stereo analogue input and output

- S/PDIF Output

- Supports the following sample frequencies: 44.1, 48, 88.2, 96, 176.4*, 192kHz

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

* S/PDIF Output at 176.4kHz not supported due to mclk requirements (see changelog)


Firmware Detail
===============

Overview
--------
The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

When connected via a full-speed hub the device falls back to operate at Audio 1.0 at full-speed.  A different PID is used to 
avoid Windows driver caching issues.

Additionally, build options are provided for Audio Class 1.0.  To remain compliant this causes the device to run at full-speed.

When running at full-speed sample-frequency restrictions are enforced to ensure fitting within the band-width restrictions of 
full-speed USB.

The firmware provides stereo input and output via I2S and stereo output via S/PDIF.  Build options are provided to enable/disable 
input and output functionality.

In Field Firmware Upgrade
-------------------------
The firmware provides a DFU interface compliant to the USB DFU Device Class.  An example host application is provided for OSX.  See README in example application for usage.  The Thesycon USB Audio Class 2.0 driver for Windows provides DFU functionality and includes an example application.


Known Issues
============

-  Buttons A and B currently have no functionality attached to them

-  OSX driver emits zero samples on occasion when run in Async mode, please report issues to Apple 

-  Windows XP volume control very sensitive.  The Audio 1.0 driver built into Windows XP (usbaudio.sys) does not properly support master volume AND channel volume controls, leading to a very sensitive control.  Descriptors can be easily modified to disable master volume control if required (one byte - bmaControls(0) in Feature Unit descriptors)

-  88.2kHz and 176.4kHz sample frequencies are not exposed in Windows control panels.  This is due to known OS restrictions

-  CODEC (CS4270) auto-mute/soft-ramp feature can cause volume ramp at start of playback.  These features cannot be disabled on the reference board since CODEC is used in Hardware Mode

-  In some circumstances a single click on the output near to stream start has been observed.  This artifact only occurs once and only occurs on Windows using Audio Class 1.0.


Host System Requirements
========================

- Mac OSX version 10.6 or later

- Windows XP, Vista or 7 with Thesycon Audio Class 2.0 driver for Windows (contact XMOS for details)
  

Instructions for Programming XMOS USB Audio Reference Design Flash
==================================================================

To upgrade the firmware, firstly:

1.    Plug the USB Audio board into your Mac
2.    Connect the XTAG2 to the USB Audio board and plug the XTAG2 into your PC or Mac. 

The upgrade process can be performed using the XMOS Development environment or command line based tools.

Using Command Line Tools:

1.    Open the XMOS command line tools (Desktop Tools Prompt)
2.    Execute the following command:  xflash <binary>.xe

Using the XMOS Development Environment:

1.    Start the XMOS Development Environment and open a workspace 
2.    Goto File->Import, select C/XC->C/XC Executable
3.    Click Browse and select the new firmware (.xe) file
4.    Click Next
5.    Click Finish
6.    A Debug Configurations window will appear, click Close
7.    Click Run->Run Configurations
8.    Double-click Flash Programmer to create a new configuration
9.    Browse for both the xe file in both the Project and C/XC Application boxes
10    Ensure the XTAG-2 device appears in the device list.  
11.   Click Run
 
Output similar to the following will be generated in the console window:

Building flash images... 
portDeclsXC_a03532: Warning: Port
"__xccomp_internal_portHolder_0_anon_3" is not placed on specific core 
(support may later be deprecated).
portDeclsXC_a03532: Warning: Port
"__xccomp_internal_portHolder_0_anon_2" is not placed on specific core 
(support may later be deprecated).
portDeclsXC_a03532: Warning: Port
"__xccomp_internal_portHolder_0_anon_1" is not placed on specific core 
(support may later be deprecated).
portDeclsXC_a03532: Warning: Port
"__xccomp_internal_portHolder_0_anon_0" is not placed on specific core 
(support may later be deprecated).
Programmer started
Program page at address:
  0x000000...            
  0x000000...  (validated)
  0x000400...            
  0x000400...  (validated)
  0x000800...            
  0x000800...  (validated)
  0x000c00...            
  0x000c00...  (validated)
  0x001000...            
  0x001000...  (validated)
  0x001400...            
  0x001400...  (validated)
  0x001800...            
  0x001800...  (validated)
  0x001c00...            
  0x001c00...  (validated)
  0x002000...            
  0x002000...  (validated)
  0x002400...            
  0x002400...  (validated)
  0x002800...            
  0x002800...  (validated)
  0x002c00...            
  0x002c00...  (validated)
  0x003000...            
  0x003000...  (validated)
  0x003400...            
  0x003400...  (validated)
  0x003800...            
  0x003800...  (validated)
  0x003c00...            
  0x003c00...  (validated)
  0x004000...            
  0x004000...  (validated)
  0x004400...            
  0x004400...  (validated)
  0x004800...            
  0x004800...  (validated)
  0x004c00...            
  0x004c00...  (validated)
  0x005000...            
  0x005000...  (validated)
 
SPI flash programming completed successfully.

Disconnect the XTAG2 and power-cycle the Audio board to boot the new firmware.


Intructions for Building Project 
================================

Using XMOS Development Environment (XDE):

To install, open the XDE Eclipse IDE and perform the following steps:

   * Select the "Import" item from the "File" menu
   * Select "General" -> "Existing Projects into Workspace" and click "Next"
   * Click on "Browse" next to "Select archive file" and select the
     zip file.
   * Make sure the projects you want to import are ticked in the
     "Projects:" list. Import all the components and whichever
     applications you are interested in. 
   * Click on "Finish"

To build, select the application you wish to build in the Project
Explorer window and click on build icon. To run an application: select
the .xe file in the bin/ directory of that application project, right
click and select "Run As..."

Using XMOS Command Line Tools:

To install, unzip the package zip. To build an application change into
that application directory and execute the command:

   xmake all

The generated executable will be placed in the bin/ sub-directory. To
run execute the command:

   xrun bin/[binary file].xe


Changelog
=========
See CHANGELOG


Support
=======

For all support issues please contact support@xmos.com


