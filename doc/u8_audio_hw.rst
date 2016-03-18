.. _usb_audio_sec_u8_audio_hw:


USB Multi-function Audio (MFA) Kit
----------------------------------

`The XMOS Multi-function Audio kit <http://www.xmos.com/products/reference-designs/mfa>`_ 
(XK-USB-AUDIO-U8-2C-AB) is a hardware reference design available from XMOS based on a single 
tile XMOS U-series device.

The kit is made up of two boards:
    - A main board which includes the XMOS U-series device and all audio hardware
    - A "USB Slice" board which contains USB connectivity

The separate USB slice board allows flexibility in the connection method to the USB audio 
source/sink as well as other functionality such as 3rd party authentication ICs and any required 
USB switching.  This also means the XMOS device can be used as a USB device or host using the same
main board.

This document addresses the combination of the main board with the USB AB slice (part numbers 
XK-USB-AUDIO-U8-2C and XA-SK-USB-AB respectively).  This provides a standard USB Audio device 
hardware configuration using the B socket on the USB AB slice.


.. _usb_audio_mfa_hw_diagram:

.. figure:: images/block_diagram_mfa.*
     :align: center
     :width: 100%

     Multi-function Audio Kit Block Diagram


The core board includes a U-Series device with integrated USB PHY, a stereo DAC (with support for 
Direct Stream Digital) and a stereo ADC.  Both ADC and DAC support sample frequencies up to 192kHz.  
As well as analogue channels the main board also has MIDI input and output connectors and a COAX 
connector for S/PDIF output.

In addition the main board also includes two LEDs, two buttons and one two-position switch for 
use by the user application.
