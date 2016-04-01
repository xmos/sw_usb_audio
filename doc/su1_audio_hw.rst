.. _usb_audio_sec_su1_audio_hw:


USB Audio 2.0 DJ Kit
--------------------

.. note::
        This hardware should not be used for the basis of a new design.

`The XMOS USB Audio 2.0 DJ kit (XR-USB-AUDIO-2.0-4C) <https://www.xmos.com/support/boards?product=15404>`_ is a
hardware reference design available from XMOS based on the XMOS U8 device. 

The DJ naming simply comes from the fact the board has 4 input and 4 output audio channels - a common configuration for a DJ controller.

The kit is made up of two boards a "core" board and an "audio slice" board.  Part numbers XP-SKC-SU1 and XA-SK-AUDIO respectively.

The core board includes a U-Series device with integrated USB PHY.  The audio slice board is equipped with two stereo audio CODECs giving 4 channels of input and 4 channels of output at sample frequencies up to 192kHz.

In addition to analogue channels the audio slice board also has MIDI input and output connectors and a COAX connector for S/PDIF output.
