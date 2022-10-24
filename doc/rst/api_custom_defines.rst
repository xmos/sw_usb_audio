
.. _sec_xua_conf_api:

Configuration Defines
---------------------

An application using the USB audio framework needs to have defines set for configuration.
Defaults for these defines are found in ``module_usb_audio`` in ``devicedefines.h``.

These defines should be over-ridden in the mandatory  ``customdefines.h`` file or in ``Makefile``
for a relevant build configuration. 

This section fully documents all of the setable defines and their default values (where appropriate).  

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
.. doxygendefine:: FULL_SPEED_AUDIO_2


System Feature Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MIDI
....

.. doxygendefine:: MIDI
.. doxygendefine:: MIDI_RX_PORT_WIDTH

S/PDIF
......

.. doxygendefine:: SPDIF_TX
.. doxygendefine:: SPDIF_TX_INDEX
.. doxygendefine:: SPDIF_RX
.. doxygendefine:: SPDIF_RX_INDEX

ADAT
....

.. doxygendefine:: ADAT_RX
.. doxygendefine:: ADAT_RX_INDEX

PDM Microphones
...............

.. doxygendefine:: NUM_PDM_MICS

DFU
...

.. doxygendefine:: DFU

.. .. doxygendefine:: DFU_FLASH_DEVICE

HID
...

.. doxygendefine:: HID_CONTROLS


CODEC Interface
...............

.. doxygendefine:: CODEC_MASTER


USB Device Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. doxygendefine:: VENDOR_STR
.. doxygendefine:: VENDOR_ID
.. doxygendefine:: PRODUCT_STR
.. doxygendefine:: PRODUCT_STR_A2
.. doxygendefine:: PRODUCT_STR_A1
.. doxygendefine:: PID_AUDIO_1
.. doxygendefine:: PID_AUDIO_2
.. doxygendefine:: BCD_DEVICE


Stream Formats
~~~~~~~~~~~~~~

Output/Playback
...............

.. doxygendefine:: OUTPUT_FORMAT_COUNT

.. doxygendefine:: STREAM_FORMAT_OUTPUT_1_RESOLUTION_BITS
.. doxygendefine:: STREAM_FORMAT_OUTPUT_2_RESOLUTION_BITS
.. doxygendefine:: STREAM_FORMAT_OUTPUT_3_RESOLUTION_BITS

.. doxygendefine:: HS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES
.. doxygendefine:: HS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES
.. doxygendefine:: HS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES

.. doxygendefine:: FS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES
.. doxygendefine:: FS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES
.. doxygendefine:: FS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES

.. doxygendefine:: STREAM_FORMAT_OUTPUT_1_DATAFORMAT
.. doxygendefine:: STREAM_FORMAT_OUTPUT_2_DATAFORMAT
.. doxygendefine:: STREAM_FORMAT_OUTPUT_3_DATAFORMAT

Input/Recording
...............
.. doxygendefine:: INPUT_FORMAT_COUNT

.. doxygendefine:: STREAM_FORMAT_INPUT_1_RESOLUTION_BITS

.. doxygendefine:: HS_STREAM_FORMAT_INPUT_1_SUBSLOT_BYTES

.. doxygendefine:: FS_STREAM_FORMAT_INPUT_1_SUBSLOT_BYTES

.. doxygendefine:: STREAM_FORMAT_INPUT_1_DATAFORMAT

Volume Control
~~~~~~~~~~~~~~

.. doxygendefine:: OUTPUT_VOLUME_CONTROL
.. doxygendefine:: INPUT_VOLUME_CONTROL
.. doxygendefine:: MIN_VOLUME
.. doxygendefine:: MAX_VOLUME
.. doxygendefine:: VOLUME_RES

Mixing Parameters
~~~~~~~~~~~~~~~~~

.. doxygendefine:: MIXER
.. doxygendefine:: MAX_MIX_COUNT
.. doxygendefine:: MIX_INPUTS
.. doxygendefine:: MIN_MIXER_VOLUME
.. doxygendefine:: MAX_MIXER_VOLUME
.. doxygendefine:: VOLUME_RES_MIXER

Power
~~~~~

.. doxygendefine:: SELF_POWERED
.. doxygendefine:: BMAX_POWER

