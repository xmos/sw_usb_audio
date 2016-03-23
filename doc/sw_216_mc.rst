
.. _usb_audio_sec_216_audio_sw:


The xCORE-200 Multi-Channel Audio Board
---------------------------------------

An application of the USB audio framework is provideed specifically for the hardware described in
:ref:`usb_audio_sec_hw_216_mc` and is implemented on an xCORE-200-series dual tile device.  

The application assumes a standard USB B socket (i.e. USB device) is provided as the USB connectivity
method.  The related code can be found in `app_usb_aud_xk_216_mc`.

The design supports upto 8 channels of analogue audio input/output at sample-rates up to 192kHz

channels of audio input and output at sample frequencies up to
192kHz and uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * S/PDIF Transmitter
 * MIDI

The software layout is the identical to the single tile L-Series Multi-channel Reference Design 
and therefore the diagram :ref:`usb_audio_l2_threads` shows the software arrangement of the code 
running on the XS1-U chip.

As with the L-Series, each unit runs in a single core concurrently with the others units. The 
lines show the communication between each functional unit. 

Clocking and Clock Selection
+++++++++++++++++++++++++++++

The XA-SK-AUDIO8 double-slot slice includes two options for master clock generation:

    * A single oscillator with a Phaselink PLL to generate fixed 24.576MHz and 22.5792MHz 
      master-clocks
    * A Cirrus Logic CS2100 clock multiplier allowing the master clock to be generated from a
      XCore derived reference.

The master clock source is controlled by a mux which, in turn, is controlled by bit 1 of `PORT 4D`:

.. list-table:: Master Clock Source Selection
   :header-rows: 1
   :widths: 20 80
  
   * - Value
     - Source
   * - 0 
     - Master clock is sourced from PhaseLink PLL
   * - 1     
     - Master clock is source from Cirrus Clock Multiplier

The current version of the supplied application only supports the use of the fixed master-clocks
from the PhaseLink part.

The clock-select from the phaselink part is controlled via bit 2 of `PORT 4E`:

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

Configuration of both the DAC and ADC takes place using I2C.  The design uses the I2C component `sc_i2c <http://www.github.com/xcore/sc_i2c>`_.

The reset lines of the DAC and ADC are connected to bits 0 and 1 of `PORT 4E` respectively.

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
setting *P4E[0]* and *P4E[1]* low. It then selects the required master clock and keeps both the
DAC and ADC in reset for a period in order allow the clocks to stabilize.

The DAC and ADC are brought out of reset by setting *P4E[0]* and *P4E[1]* back high.

Various registers are then written to the ADC and DAC as required.

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed.  See :ref:`usb_audio_sec_valbuild` for details and binary naming scheme.

These fully validated build configurations are listed below. 
In practise, due to the similarities between the U-Series and L-Series feature set, it is fully
expected that all listed U-Series configurations will operate as expected on the L-Series and vice versa.


Configuration 2ioxs
~~~~~~~~~~~~~~~~~~~

This configuration runs in high-speed Audio Class 2.0 mode, has the mixer core is enabled (for
volume processing only, supports 10 channels in, 10 channels out, supports sample rates up to
192kHz and S/PDIF transmit.


