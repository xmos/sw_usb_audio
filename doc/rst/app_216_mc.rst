
.. _usb_audio_sec_216_audio_sw:


The xCORE-200 Multi-Channel Audio Board
---------------------------------------

An application of the USB audio framework is provided specifically for the hardware described in
:ref:`usb_audio_sec_hw_216_mc` and is implemented on an xCORE-200-series dual tile device.  The 
related code can be found in ``app_usb_aud_xk_216_mc``.

The design supports upto 8 channels of analogue audio input/output at sample-rates up to 192kHz 
(assuming the use of I2S). This can be further increased by utilising TDM. It also supports S/PDIF,
ADAT and MIDI input and output aswell as the mixing functionalty of ``lib_xua``.

The design uses the following tasks:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint Buffer
 * Decoupler
 * AudioHub Driver
 * Mixer
 * S/PDIF Transmitter
 * S/PDIF Receiver
 * ADAT Receiver
 * Clockgen
 * MIDI

:ref:`usb_audio_l2_threads`  shows the software layout of the USB
Audio 2.0 Multichannel Reference Design running on the `xCORE-200` device.

.. _usb_audio_l2_threads:

.. figure:: images/threads-l2-crop.*
     :width: 90%
     :align: center    

     Dual Tile xCORE-200 Series Reference Design Core Layout

Each circle depicts a task running in a single core concurrently with the others task. The 
lines show the communication between each task. 

Clocking and Clock Selection
+++++++++++++++++++++++++++++

The board includes two options for master clock generation:

    * A single oscillator with a Phaselink PLL to generate fixed 24.576MHz and 22.5792MHz 
      master-clocks
    * A Cirrus Logic CS2100 clock multiplier allowing the master clock to be generated from a
      XCore derived reference.

The master clock source is controlled by a mux which, in turn, is controlled by bit 5 of `PORT 8C`:

.. list-table:: Master Clock Source Selection
   :header-rows: 1
   :widths: 20 80
  
   * - Value
     - Source
   * - 0 
     - Master clock is sourced from PhaseLink PLL
   * - 1     
     - Master clock is source from Cirrus Clock Multiplier

The clock-select from the phaselink part is controlled via bit 7 of `PORT 8C`:

.. list-table:: Master Clock Frequency Select
   :header-rows: 1
   :widths: 20 80
  
   * - Value
     - Frequency
   * - 0 
     - 24.576MHz
   * - 1     
     - 22.579MHz

DAC and ADC Configuration
+++++++++++++++++++++++++

The board is equipped with a single multi-channel audio DAC (Cirrus Logic CS4384) and a single
multi-channel ADC (Cirrus Logic CS5368) giving 8 channels of analogue output and 8 channels of 
analogue input.

Configuration of both the DAC and ADC takes place using I2C.  The design uses the I2C lib
`lib_i2c <http://www.github.com/xmos/lib_i2c>`_.

The reset lines of the DAC and ADC are connected to bits 1 and 6 of `PORT 8C` respectively.

AudioHwInit()
+++++++++++++

The :c:func:`AudioHwInit()` function is implemented to perform the following: 

    * Initialise the I2C master software module
    * Puts the audio hardware into reset
    * Enables the power to the audio hardware
    * Select the PhaseLink PLL as the audio master clock source.

AudioHwConfig()
+++++++++++++++

The :c:func:`AudioHwConfig()` function is called on every sample frequency change. 

The :c:func:`AudioHwConfig` function first puts the both the DAC and ADC into reset by
setting *P8C[1]* and *P8C[6]* low. It then selects the required master clock and keeps both the
DAC and ADC in reset for a period in order allow the clocks to stabilize.

The DAC and ADC are brought out of reset by setting *P8C[1]* and *P8C[6]* back high.

Various registers are then written to the ADC and DAC as required.

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed in the Makefile.  See :ref:`usb_audio_sec_valbuild` for details and general information binary naming scheme.

These fully validated build configurations are enumerated in the supplied Makefile

In practise, due to the similarities between the `xCORE-200` and `xCORE.ai` series feature set, it is fully
expected that all listed `xCORE-200` series configurations will operate as expected on the `xCORE.ai` series and vice versa.

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
   * - USB Sync Mode
     - async: A
     - sync: S
   * - Input 
     - enabled: i (channel count)
     - disabled: x
   * - Output
     - enabled: i (channel count)
     - disabled: x
   * - MIDI
     - enabled: m
     - disabled: x
   * - S/PDIF input
     - enabled: s
     - disabled: x
   * - S/PDIF input
     - enabled: s
     - disabled: x
   * - ADAT input
     - enabled: a
     - disabled: x
   * - ADAT output
     - enabled: a
     - disabled: x
   * - DSD output
     - enabled: d
     - disabled: x

e.g. A build configuration named 2AMi10o10xsxxx would signify: Audio class 2.0 running in asynchronous mode. `xCORE` is 
I2S master. Input and output enabled (10 channels each), no MIDI, S/PDIF input, no S/PDIF output, no ADAT or DSD.

In addition to this some terms may be appended onto a build configuration name to signify additional options. For
example, `tdm` may be appended to the build configuration name to indicate the I2S mode employed.
