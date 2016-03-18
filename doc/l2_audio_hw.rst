USB Audio 2.0 Multichannel Reference Design
-------------------------------------------

The `USB Audio 2.0 Multichannel Reference Design (XR-USB-AUDIO-2.0-MC) <https://www.xmos.com/support/boards?product=14771>`_ is a hardware reference design available from XMOS based on the XMOS L16 device (previously named L2) 
 
:ref:`usb_audio_l2_hw_diagram` shows the block layout of the USB Audio 2.0 Multichannel Reference Design board.

The board supports six analogue inputs and eight analogue outputs (via a CS4244 CODEC), digital input and output (via coax and optical connectors) and MIDI input and output. For full details please refer to `USB Audio 2.0 Reference Design, XS1-L2 Edition Hardware Manual <https://www.xmos.com/download/public/USB-Audio-2.0-MC-Hardware-Manual%281.6%29.pdf>`_.

.. _usb_audio_l2_hw_diagram:

.. figure:: images/l2_block_diagram.*
     :align: center
     :width: 100%

     USB Audio 2.0 Multichannel Reference Design Block Diagram

The reference board has an associated firmware application that uses the USB Audio 2.0 software reference
platform. Details of this application can be found in section :ref:`usb_audio_sec_l2_audio_sw`.

|newpage|
