
.. _usb_audio_sec_su1_audio_sw:

The USB Audio 2.0 DJ Kit (U-Series)
-------------------------------------------

The USB Audio 2.0 Reference Design is an application of the USB audio framework specifically for the
hardware described in :ref:`usb_audio_sec_su1_audio_hw` and is implemented on the U-Series single
tile device (500MIPS). The software design supports four channels of audio at sample frequencies up
to 192kHz and uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * S/PDIF Transmitter *or* MIDI

The software layout is the identical to the single tile L-Series Reference Design and therefore the
diagrams :ref:`usb_audio_l1_threads-spdif` and :ref:`usb_audio_l1_threads-midi` show the software
layout of the code running on the XS1-U chip.

As with the L-Series, each unit runs in a single core concurrently with the others units.

Due to the MIPS requirement of the USB driver (see :ref:`usb_audio_sec_resource_usage`), only six
cores can be run on the single tile L-Series device so only one of S/PDIF transmit or MIDI can be
supported. 

Clocking and Clock Selection
+++++++++++++++++++++++++++++

The actual hardware involved in the clock generation is somewhat different to the single tile
L-Series board.  Instead of two separate oscillators and switching logic a single oscillator 
with a Phaselink PLL is used to generate fixed 24.576MHz and 22.5792MHz master-clocks.

This makes no change for the selection of master-clock in terms of software interaction: A single
pin is (bit 1 of port 4C) is still used to select between the two master-clock frequencies.

The advantages of this system are fewer components and a smaller board area.

When changing sample frequency, the :c:func:`CodecConfig` function first puts the CODEC into reset 
by setting *P4C[2]* low. It selects the required master clock  and keeps the CODEC in reset for 1ms 
to allow the clocks to stabilize.
The CODEC is brought out of reset by setting *P4C[2]* back high.

CODEC Configuration
+++++++++++++++++++

The board is equipped with two stereo audio CODECs (Cirrus Logic CS4270) giving 4 channels of input
and 4 channels of output. Configuration of these CODECs takes place using I2C, with both sharing 
the same I2C bus. The design uses the open source I2C component `sc_i2c <http://www.github.com/xcore/sc_i2c>`_

U-Series ADC
+++++++++++++

The codebase includes code exampling how the ADC built into the U-Series device can be used.  
Once setup a pin is used to cause the ADC to sample, this sample is then sent via a channel to the
xCORE device.

On the DJ kit the ADC is clocked via the same pin as the I2S LR clock.  Since this means that a ADC
sample is received every audio sample the ADC is setup and it's data received in the audio driver
core (``audio.xc``). 

The code simply writes the ADC value to the global variable ``g_adcVal`` for use elsewhere in the
program as required.  The ADC code is enabled by defining ``SU1_ADC_ENABLE`` as ``1``.  

HID Example
+++++++++++

The codebase includes an example of a HID volume control implementation based on ADC data.  This
code should be considered an example only since an absolute ADC input does not serve as an ideal
input to a relative HID volume control.  Buttons (such as that on the single tile L-Series board) 
or a Rotary Encoder would be a more fitting choice of input component.

This code is enabled if ``HID_CONTROLS``, ``SU1_ADC_ENABLE`` and ``ADC_VOL_CONTROL`` are all
defined as ``1``.

The ``Vendor_ReadHIDButtons()`` function simply looks at the value from the ADC, if is near the
maximum value it reports a volume up, near the minimum value a volume down is reported.  If the
ADC value is mid-range no event is reported.  The code is shown below:

.. literalinclude:: sw_usb_audio/app_usb_aud_skc_su1/src/extensions/vendorhid.xc
   :start-after: #define ADC_MIN
   :end-before: #endif

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`usb_audio_sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed.  See :ref:`usb_audio_sec_valbuild` for details and binary naming scheme.

These fully validated build configurations are listed below. 
In practise, due to the similarities between the U-Series and L-Series feature set, it is fully 
expected that all listed U-Series configurations will operate as expected on the L-Series and vice versa.


Configuration 2ioxs
~~~~~~~~~~~~~~~~~~~

This configuration runs in high-speed Audio Class 2.0 mode, has the mixer disabled, supports 2 channels in, 2
channels out, supports sample rates up to 192kHz and S/PDIF transmit.

Configuration 2iomx
~~~~~~~~~~~~~~~~~~~

This configuration disables S/PDIF and enables MIDI.

This configuration can be achieved by in the Makefile by defining ``SPDIF`` as zero::
    
    -DSPDIF=0

and ``MIDI`` as 1::

    -DMIDI=1

Configuration 2ixxx
~~~~~~~~~~~~~~~~~~~

This configuration is input only (``NUM_USB_CHAN_OUT`` set to zero).  I.e. a microphone application or similar.


Configuration 1ioxs
~~~~~~~~~~~~~~~~~~~~

This configuration is similar to the first configuration apart from it runs in Audio 1.0 over full-speed USB.

This is achieved in the Makefile by::

    -DAUDIO_CLASS=1

Configuration 1xoxs
~~~~~~~~~~~~~~~~~~~~

This configuration is similar to the configuration above in that it runs in Audio 1.0 over full-speed USB.  
However, the it is output only (i.e. the input path is disabled with ``-DNUM_USB_CHAN_IN=0``

