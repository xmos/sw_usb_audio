.. _usb_audio_interface_sg_hw:

XMOS USB Audio Interface Hardware Development Kit (XS1-L1)
----------------------------------------------------------

The following diagram shows the block layout of the XMOS USB Audio
Interface Development Kit. The main purpose of the XS1-L1 is to
provide a USB audio interface to the USB PHY and route the audio to
the audio CODEC. 

.. figure:: images/l1_ios_block_diagram.*
   :align: center

   XMOS USB Audio Interface Development Kit Block Diagram

The board has an associated firmware application that uses the USB audio 2.0 software reference
platform. Details of this application can be found in :ref:`sec_l1_ios_audio_sw`.

This platform is based on the L1 USB Audio reference design with a number of changes:

   * Reduced BOM

      * Uses XS1-L1-48TQFP

   * Low speed IO expander provided by shift registers to increase the number of IO available

   * MIDI interface added

   * iOS support added

      * Apple co-processor added on I2C bus

         * The I2C bus shares ports with the MIDI interface and is selected via a line on the IO expander

      * Apple 30 pin connector available on an add on board

      * USB host ID resistor and accessory detect controlled on an IO expander output

   * USB switch to select between 30 pin connector or USB B connector. Controlled by IO expander output.
