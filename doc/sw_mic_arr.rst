
.. _usb_audio_sec_mic_arr_audio_sw:


The xCORE-200 Array Microphone Board
------------------------------------

An application of the USB audio framework is provided specifically for the hardware described in
:ref:`usb_audio_sec_hw_arr_mic` and is implemented on an xCORE-200-series dual tile device.  The 
related code can be found in `app_usb_aud_array_mic`.

The design supports upto 2 channels of analogue audio output at sample-rates from the
on-board DAC. The design also supports input from the 7 PDM microphones.

The design uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * PDM Microphone integration

The software layout is the identical to the dual tile L-Series Multi-channel Reference Design 
and therefore the diagram :ref:`usb_audio_l2_threads` shows the software arrangement of the code 
running on the xCORE-200 device.

As with the L/U-Series, each unit runs in a single core concurrently with the others units. The 
lines show the communication between each functional unit. 

Clocking and Clock Selection
+++++++++++++++++++++++++++++

The board includes an external fractional-N clock multiplier (Cirrus Logic CS2100) for audio clock generation.

This allows the audio master clock to be generated from an reference clock provided by the xCORE, optionally derived
from some external source e.g. an incoming digital steam.

.. note::

    This functionality is primarily included on the board to allow for Ethernet AVB, where syncing to an external lock 
    is required. In the USB audio design the IC is simply used for master clock generation.

.. note::

    The system wide audio master-clock is connected to the AUX output of the CS2100 part. By default, without configuration, 
    the CS2100 part outputs the 24.576 REF input to this output.

The clock multiply ratio is programmed into the CS2100 via the I2C bus.


DAC Configuration
+++++++++++++++++

The board is equipped with a single stereo audio DAC with integrated headphone amplifier (Cirrus Logic CS43L21)

Configuration of both the DAC takes place using I2C.  The design uses the I2C component
`sc_i2c <http://www.github.com/xcore/sc_i2c>`_.

The reset lines of the DAC is connected to bits 0 `PORT 4F`.

AudioHwInit()
+++++++++++++

The :c:func:`AudioHwInit()` function is called on power up and is implemented to perform the following: 

    * Configures a port to drive a fixed clock to the CS2100 `CLK_IN` input
    * Puts the DAC into reset
    * Initialise the I2C master software module
    * Initialises the CS2100 part over I2C
    * Configures the CS2100 part to output a ratio for a suitable initial master clock frequency (`DEFAULT_MCLK_FREQ`)

AudioHwConfig()
+++++++++++++++

The :c:func:`AudioHwConfig()` function is called on every sample frequency change. 

The :c:func:`AudioHwConfig` function first puts the both the DAC/headphone-amp and into reset by writing to `PORT 4F`. 

It then sets the required ratio in the CS2100 via I2C based on the ``mClk`` parameter. After a delay, in order to allow 
the master clock from the CS2100 to settle the DAC is take out of reset.  The DAC is then configured via I2C, this primarily involves
switching the DAC into I2S slave mode

|newpage|

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed in the Makefile.  See :ref:`usb_audio_sec_valbuild` for details and binary naming scheme.

These fully validated build configurations are enumerated in the supplied Makefile

In practise, due to the similarities between the U/L/xCORE-200 Series feature set, it is fully
expected that all listed U-Series configurations will operate as expected on the L-Series and vice versa.

The build configuration naming scheme employed in the makefile is as follows:

.. list-table:: Build config naming scheme
   :header-rows: 1
   :widths: 20 80 80
  
   * - Feature
     - Option 1
     - Option 2
   * - Audio Class
     - 1
     - 2
   * - Input 
     - enabled: i (channel count)
     - disabled: x
   * - Output
     - enabled: i (channel count)
     - disabled: x
   * - MIDI
     - enabled: m
     - disabled: x
   * - SPDIF output
     - enabled: s
     - disabled: x
   * - SPDIF input
     - enabled: s
     - disabled: x
   * - ADAT output
     - enabled: a
     - disabled: x
   * - ADAT input
     - enabled: a
     - disabled: x
   * - DSD output
     - enabled: d
     - disabled: x

e.g. A build config named 2i10o10xsxxx would signify: Audio class 2.0, input and output enabled (10 channels each), no MIDI SPDIF output, no SPDIF input, no ADAT or DSD

In addition to this the terms `tdm` or `slave` may be appended to the build configuration name to indicate the I2S mode employed.
