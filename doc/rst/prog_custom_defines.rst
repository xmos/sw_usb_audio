:orphan:

.. _usb_audio_sec_custom_defines_api:

Custom Defines
==============

An application using the USB audio framework needs to have a defines
file called ``customdefines.h``. This file can set the following defines:

System Feature Configuration
----------------------------

.. tabularcolumns:: p{0.3\linewidth}p{0.4\linewidth}p{0.2\linewidth}

.. list-table::
   :header-rows: 1
   :class: longtable

   * - Define
     - Description
     - Default

   * - ``INPUT``
     - Define for enabling audio input, in descriptors, buffering and
       so on.
     - defined

   * - ``DFU``
     - Define to enable DFU interface. Requires a custom driver for
       Windows.
     - defined

   * - ``DFU_CUSTOM_FLASH_DEVICE``
     - Define to enable use of custom
       flash device for DFU interface.
     - not defined

   * - ``MIDI``
     - Define to enable MIDI input and output.
     - defined

   * - ``CODEC_SLAVE``
     - If defined the CODEC acts as I2S slave
       (and the XCORE Tile as master) otherwise the CODEC acts as master.
     - defined

   * - ``NUM_USB_CHAN_IN``
     - Number of audio channels the USB audio
       interface has from host to the device.
     - 10

   * - ``NUM_USB_CHAN_OUT``
     - Number of audio channels the USB audio
       interface has from device to host.
     - 10

   * - ``MAX_FREQ``
     - Maximum frequency device runs at in Hz
     - 96000

   * - ``I2S_CHANS_DAC``
     - Number of I2S audio channels output to the
       codec. This must be a multiple of 2.
     - 8

   * - ``I2S_CHANS_ADC``
     - Number of I2S audio channels input from the codec.
       This must be a multiple of 2.
     - 8

   * - ``SPDIF``
     - Define to Enable S/PDIF output.  If OUTPUT is not
       defined, zero-ed samples are emitted. The S/PDIF audio channels will
       be two channels immediately following ``I2S_CHANS_DAC``.
     - defined

   * - ``SPDIF_RX``
     - Define to enable S/PDIF input.
     - not defined

   * - ``ADAT_RX``
     - Define to enable ADAT input.
     - not defined

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
--------------------------------


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
