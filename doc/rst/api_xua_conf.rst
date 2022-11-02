
.. _sec_xua_conf_api:

Configuration Defines
---------------------

An application using the USB audio framework provided by ``lib_xua``  needs to have defines set for configuration.
Defaults for these defines are found in ``lib_xua`` in ``xua_conf_default.h``.

An application should override these defines in an optional ``xua_conf.h`` file or in the ``Makefile``
for a relevant build configuration. 

This section documents commonly used defines, for full listings and documentation see the ``lib_xua``.


Code location (tile)
~~~~~~~~~~~~~~~~~~~~

.. doxygendefine:: AUDIO_IO_TILE
.. doxygendefine:: XUD_TILE
.. doxygendefine:: MIDI_TILE
.. doxygendefine:: PLL_REF_TILE
.. doxygendefine:: SPDIF_TX_TILE

Channel Counts
~~~~~~~~~~~~~~

.. doxygendefine:: NUM_USB_CHAN_OUT 
.. doxygendefine:: NUM_USB_CHAN_IN 
.. doxygendefine:: I2S_CHANS_DAC 
.. doxygendefine:: I2S_CHANS_ADC 
.. doxygendefine:: DSD_CHANS_DAC

Frequencies and Clocks 
~~~~~~~~~~~~~~~~~~~~~~

.. doxygendefine:: MAX_FREQ
.. doxygendefine:: MIN_FREQ
.. doxygendefine:: MCLK_441
.. doxygendefine:: MCLK_48

Audio Class
~~~~~~~~~~~

.. doxygendefine:: AUDIO_CLASS

System Feature Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MIDI
....

.. doxygendefine:: MIDI
.. doxygendefine:: MIDI_RX_PORT_WIDTH

S/PDIF
......

.. doxygendefine:: XUA_SPDIF_TX_EN
.. doxygendefine:: SPDIF_TX_INDEX
.. doxygendefine:: XUA_SPDIF_RX_EN
.. doxygendefine:: SPDIF_RX_INDEX

ADAT
....

.. doxygendefine:: XUA_ADAT_RX_EN
.. doxygendefine:: ADAT_RX_INDEX

PDM Microphones
...............

.. doxygendefine:: XUA_NUM_PDM_MICS

DFU
...

.. doxygendefine:: XUA_DFU_EN

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

Volume Control
~~~~~~~~~~~~~~

.. doxygendefine:: OUTPUT_VOLUME_CONTROL
.. doxygendefine:: INPUT_VOLUME_CONTROL

Mixing Parameters
~~~~~~~~~~~~~~~~~

.. doxygendefine:: MIXER
.. doxygendefine:: MAX_MIX_COUNT
.. doxygendefine:: MIX_INPUTS

Power
~~~~~

.. doxygendefine:: XUA_POWERMODE

