.. _usb_audio_sec_hw_u16_audio8:

U16 Multi-Channel USB Audio Kit
-------------------------------

.. note::
        It is not recommended to use this hardware as a basic for a new design


`The XMOS U16 Multi-Channel USB Audio kit <http://www.xmos.com/usbaudio16mc>`_ is a hardware
development platform available from XMOS based on a dual tile XMOS U-series device.

The kit is made up of three boards:
    - A sliceKIT core board which includes the XMOS U-series device (XP-SKC-U16)
    - A "USB Slice" board which contains USB connectivity (XA-SK-USB-AB)
    - A double-slot slice card including audio hardware and connectors (XA-SK-AUDIO8)

The separate USB slice board allows flexibility in the connection method to the USB audio 
source/sink as well as other functionality such as 3rd party authentication ICs and any required 
USB switching.  This also means the XMOS device can be used as a USB device or host using the same
main board.

This document addresses the combination of the main board with the USB AB slice (part numbers 
XP-SKC-U16 and XA-SK-USB-AB respectively).  This provides a standard USB Audio device 
hardware configuration using the B socket on the USB AB slice.

The core board includes a U-Series device with integrated USB PHY and required supporting componentry.

Please note, for correct operation the following core-board jumper settings are required:

    * J14 (DIA/ALT) should be set to ALT

    * J15 (D12 XOVER) should be set to ON

The double-slot audio slice (XA-SK-AUDIO8) includes separate multi-channel DAC and ADC providing 8
channels of both analogue output and input. Both DAC and ADC devices support sample frequencies up
to 192kHz with the DAC supporting Direct Stream Digital (DSD).

As well as analogue channels the audio-slice also has MIDI input and output connectors and both COAX 
and optical connectors for digital output.

Additionally the slice also includes an LED matrix and three push-buttons for use by the user application.
