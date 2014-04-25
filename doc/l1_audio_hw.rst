.. _usb_audio_sec_l1_audio_hw:


USB Audio 2.0 Reference Design
------------------------------

The `USB Audio 2.0 Reference Design <http://www.xmos.com/products/development-kits/usbaudio2>`_ is a
hardware reference design available from XMOS based on an XMOS L8 device.  The diagram in  
:ref:`usb_audio_l1_hw_diagram` shows the block layout of the USB Audio
2.0 Reference Design board. The main purpose of the XS1 L-Series device is to
provide a USB Audio interface to the USB PHY and route the audio to
the audio CODEC and S/PDIF output. Note that although the software
supports MIDI, there are no MIDI connectors on the board. 

For full details please refer to the `USB Audio 2.0 Ref Design XS1-L1 Hardware Manual <https://www.xmos.com/published/usb-audio-20-ref-design-xs1-l1-hardware-manual>`_.

.. _usb_audio_l1_hw_diagram:

.. figure:: images/l1_block_diagram.*
   :align: center
   :width: 100%

   USB Audio 2.0 Reference Design Block Diagram


The reference board has an associated firmware application that uses the USB Audio 2.0 software reference
platform. Details of this application can be found in section :ref:`usb_audio_sec_l1_audio_sw`.

|newpage|
