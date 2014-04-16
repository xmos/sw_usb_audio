
.. _usb_audio_sec_su1_audio_sw:

The Mult-function Audio Kit (U-Series)
--------------------------------------

Proviced is an application of the USB audio framework specifically for the hardware described in :ref:`usb_audio_sec_u8_audio_hw` and is implemented on the U-Series single tile device (500MIPS).  The application assumes a standard USB B socket (i.e. USB device) is attached as the USB connectivity method.

The software design supports 2 channels channels of
audio at sample frequencies up to 192kHz and uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * S/PDIF Transmitter *or* MIDI

The software layout is the identical to the single tile L-Series Reference Design and therefore the diagrams :ref:`usb_audio_l1_threads-spdif` and :ref:`usb_audio_l1_threads-midi` show the software layout of the code running on the XS1-U chip.

As with the L-Series, each unit runs in a single core concurrently with the others units. The lines show the
communication between each functional unit. 

Due to the MIPS requirement of the USB driver 
(see :ref:`usb_audio_sec_resource_usage`), only six cores can be
run on the single tile L-Series device so only one of S/PDIF transmit or MIDI
can be supported. 

Clocking and Clock Selection
+++++++++++++++++++++++++++++

A single oscillator with a Phaselink PLL is used to generate fixed 24.576MHz and 22.5792MHz master-clocks.

This makes no change for the selection of master-clock in terms of software interaction: A single pin is (bit 1 of port 32A) is used to select between the two master-clock frequencies.

When changing sample frequency, the :c:func:`AudioHwConfig` function first puts the both the DAC and ADC into reset by
setting *P4C[0]* and *P4C[1]* low. It selects the required master clock and keeps both the DAC and ADC in reset for 1ms to allow the 
clocks to stabilize.
The DAC and ADC are brought out of reset by setting *P4C[0]* and *P4C[1]* back high.

DAC and ADC Configuration
+++++++++++++++++++++++++

The board is equipped with a single stereo audio DAC (Cirrus Logic CS4392) and a single stereo ADC (Cirrus Logic 5340) giving 2 channels of input and 2 channels of output.

Configuration of the DAC takes place using I2C.  The design uses the open source I2C component `sc_i2c <http://www.github.com/xcore/sc_i2c>`_ No configuration of the ADC is required in software, it is set into slave mode via its configuration pins on the board. 

U-Series ADC
+++++++++++++

The codebase includes code exampling how the ADC built into the U-Series device can be used.  Once setup a pin is used to cause the ADC to sample, this sample is then sent via a channel to the xCORE device.

On the multi-function audio board the ADC is clocked via the same pin as the I2S LR clock.  Since this means that a ADC sample is received every audio sample the ADC is setup and it's data received in the audio driver core (``audio.xc``). 

The ADC inputs for the U8 device are simply pinned out to test point headers.  As such there is no example functionality attached to the ADC data.

HID Example
+++++++++++

The codebase includes an example of a HID controls implementation using the two buttons and switch on the multi-function audio board. 

This example code is enabled if ``HID_CONTROLS`` are all defined as ``1``.  When this define is enabled a call to the function ``Vendor_ReadHIDButtons()`` is enabled and must be implemented. Failing to do so will result in a build error.

The example ``Vendor_ReadHIDButtons()`` firstly reads the state of the buttons and switch.  These inputs are all connected to the same 4-bit port.  Since the buttons are active low and the HID report is active high the value read is inverted.  Some bitwise operations are then used to exact the individual states of the buttons and switch.

If the switch input is low (i.e. high when inverted) then the button states are shifted up into the position required perform volume up and down and written into the *hidData[]* array:

.. literalinclude:: sw_usb_audio/app_usb_aud_skc_su1/src/extensions/vendorhid.xc
   :start-after: /* Assign buttons
   :end-before: }

If the switch input is high (i.e. low when inverted) then the buttons states are used to either indicate play/pause or next/previous.  Based on counter and a small state-machine a single click on either button provides a play/pause command.  A double tap on button A or B provides a previous or next command respectively.

The full code listing is shown below:
.. literalinclude:: sw_usb_audio/app_usb_aud_skc_su1/src/extensions/vendorhid.xc
   :start-after: #define THRESH
   :end-before: typedef

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`usb_audio_sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed.  See :ref:`usb_audio_sec_valbuild` for details and binary naming scheme.

These fully validated build configurations are listed below. 
In practise, due to the similarities between the U-Series and L-Series feature set, it is fully expected that all listed U-Series
configurations will operate as expected on the L-Series and vice versa.


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

This configuration is similar to the configuration above in that it runs in Audio 1.0 over full-speed USB.  However, the it is output only (i.e. the input path is disabled with ``-DNUM_USB_CHAN_IN=0``

