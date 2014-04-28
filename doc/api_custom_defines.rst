
.. _sec_custom_defines_api:

Custom Defines
--------------

An application using the USB audio framework needs to have a defines set for configuration.
Defaults for these defines are found in ``module_usb_audio`` in ``devicedefines.h``.

These defines should be over-ridden in the mandatory  ``customdefines.h`` file or in ``Makefile``. 

The following defines can be set.

Code location (tile)
~~~~~~~~~~~~~~~~~~~~

.. doxygendefine:: AUDIO_IO_TILE

.. doxygendefine:: XUD_TILE

.. doxygendefine:: IAP_TILE

.. doxygendefine:: MIDI_TILE

Channel Counts
~~~~~~~~~~~~~~

.. doxygendefine:: NUM_USB_CHAN_OUT 

.. doxygendefine:: NUM_USB_CHAN_IN 

.. doxygendefine:: DSD_CHANS_DAC

.. doxygendefine:: I2S_CHANS_DAC 

.. doxygendefine:: I2S_CHANS_ADC 

Frequencies and Clocks 
~~~~~~~~~~~~~~~~~~~~~~

.. doxygendefine:: MAX_FREQ

.. doxygendefine:: MIN_FREQ

.. doxygendefine:: DEFAULT_FREQ

.. doxygendefine:: MCLK_441

.. doxygendefine:: MCLK_48

Audio Class
~~~~~~~~~~~

.. doxygendefine:: AUDIO_CLASS

.. doxygendefine:: AUDIO_CLASS_FALLBACK

.. doxygendefine:: FULL_SPEED_AUDIO_CLASS_2


System Feature Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MIDI
....

.. doxygendefine:: MIDI

.. doxygendefine:: MIDI_RX_PORT_WIDTH

S/PDIF
......

.. doxygendefine:: SPDIF

.. doxygendefine:: SPDIF_RX

ADAT
....

.. doxygendefine:: ADAT_RX


DFU
...

.. doxygendefine:: DFU

.. doxygendefine:: DFU_FLASH_DEVICE




.. tabularcolumns:: p{0.3\linewidth}p{0.4\linewidth}p{0.2\linewidth}

.. list-table::
   :header-rows: 1
   :class: longtable

   * - Define
     - Description
     - Default

   * - ``CODEC_SLAVE`` 
     - If defined the CODEC acts as I2S slave
       (and the XCORE Tile as master) otherwise the CODEC acts as master. 
     - defined 

   * - ``MIXER`` 
     - Define to enable the MIXER.
     - not defined 

   * - ``MIN_VOLUME``
     - The minimum volume setting above -inf. This is a signed 8.8 fixed point
       number that must be strictly greater than -128 (0x8000).
     - 0x8100

   * - ``MAX_VOLUME``
     - The maximum volume setting for the mixer in db.
       This is a signed 8.8 fixed point number.
     - 0

   * - ``VOLUME_RES``
     - The resolution of the volume control in db as a 8.8 fixed point
       number.
     - 0x100

   * - ``MIN_MIXER_VOLUME``
     - The minimum volume setting for the mixer unit above -inf. 
       This is a signed 8.8 fixed point
       number that must be strictly greater than -128 (0x8000). 
     - 0x8080

   * - ``MAX_MIXER_VOLUME``
     -  The maximum volume setting for the mixer. This is a
        signed 8.8 fixed point number. 
     -  0x0600

   * - ``VOLUME_RES_MIXER``
     - The resolution of the volume control in db as a 8.8 fixed point number. 
     - 0x080

   

USB Device Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. tabularcolumns:: p{0.3\linewidth}p{0.4\linewidth}p{0.2\linewidth}

.. list-table::
   :header-rows: 1
   :class: longtable smaller

   * - Define
     - Description
     - Default


   * - ``VENDOR_ID``
     - Vendor ID 
     - (0x20B1) 

   * - ``PID_AUDIO_2`` 
     - Product ID (Audio Class 2) 
     - N/A 

   * - ``PID_AUDIO_1`` 
     - Product ID (Audio Class 1) 
     - N/A 

   * - ``BCD_DEVICE`` 
     - Device release number in BCD form 
     - N/A 

   * - ``VENDOR_STR`` 
     - String identifying vendor 
     - XMOS 

   * - ``SERIAL_STR`` 
     - String identifying serial number 
     - "0000" 
