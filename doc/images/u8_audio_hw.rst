.. _usb_audio_sec_u8_audio_hw:


U8 Multi-function Audio Kit (U-Series)
--------------------------------------

`The XMOS Multi-function Audio kit (XS1 U-Series) <http://www.xmos.com/products/development-kits/usbaudio2>`_ is a
hardware reference design available from XMOS. 

The kit is made up of two boards
    - A main board which includes the XMOS U8 and all audio hardware
    - A "USB Slice" board which contains USB connectivity

The seperate USB slice baord allows flexibility in the connection method the the USB audio source/sink as well as other functionality such as Apple Authentication ICs and any required USB switching.  This also means the XMOS device can be used as a USB device or host using the same main board.  

This document addresses the combination of the main board with the USB B slice (part numbers XK-USB-AUDIO-U8-2C and XA-SK-USB-B respectively).  This gives a standard USB device hardware configuration

The core board includes a U-Series device with integrated USB PHY, a stereo DAC (supporting DSD) and a stereo ADC.  Both ADC and DAC support sample frequencies up to 192kHz.  Aswell as analogue channels the main board also has MIDI input and output connectors and a COAX connector for S/PDIF output.

In addition the main board also includes two LEDs, two buttons and one switch for use by the user application.
