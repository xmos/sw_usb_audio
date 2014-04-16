.. _usb_audio_sec_l1_audio_sw:

The USB Audio 2.0 Reference Design (L-Series) Software
-------------------------------------------------------

The USB Audio 2.0 Reference Design is an application of the USB audio
framework specifically for the hardware described in :ref:`usb_audio_sec_l1_audio_hw` and is implemented on the L-Series single tile device (500MIPS).
The software design supports two channels of
audio at sample frequencies up to 192kHz and uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * S/PDIF Transmitter *or* MIDI

The diagrams :ref:`usb_audio_l1_threads-spdif` and :ref:`usb_audio_l1_threads-midi`
show the software layout of the code
running on the XS1-L chip. Each unit runs in a single
core concurrently with the others units. The lines show the
communication between each functional unit. Due to the MIPS
requirement of the USB driver 
(see :ref:`usb_audio_sec_resource_usage`), only six cores can be
run on the single tile L-Series device so only one of S/PDIF transmit or MIDI
can be supported. 

.. _usb_audio_l1_threads-spdif:

.. figure:: images/threads-spdif-crop.*
     :width: 100%

     Single Tile L-Series Software Core Diagram (with S/PDIF TX)

.. _usb_audio_l1_threads-midi:

.. figure:: images/threads-midi-crop.*
     :width: 100%

     Single Tile L-Series Software Core Diagram (with MIDI I/O)


Port 32A
++++++++

Port 32A on the XS1-L device is a 32-bit wide port that has several separate
signal bit signals connected to it, accessed by multiple cores.  To this end, 
any output to this port must be *read-modify-write* i.e. to change a single bit of 
the port, the software reads the current value being driven across 32 bits, flips 
a bit and then outputs the modified value.

This method of port usage (i.e. sharing a port between cores) is outside the standard XC usage model so is implemented
using inline assembly as required.  The ``peek`` instruction is used to get the current output value on the port::

    /* Peek at current port value using port 32A resource ID */
    asm("peek %0, res[%1]":=r"(x):"r"(XS1_PORT_32A));

The required output value is then assembled using the relevant bit-wise operation(s) before the ``out`` instruction is 
used directly to output data to the port::

    /* Output to port */
    asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));


The table :ref:`usb_audio_port32A_signals` shows the signals connected to port 32A on the USB Audio Class 2.0
reference design board.  Note, they are all *outputs* from the XS1-L device.

.. _usb_audio_port32A_signals:

.. list-table:: Port 32A Signals
  :header-rows: 1
  :widths: 30 30 30

  * - Pin    
    - Port
    - Signal
  * - XD49 
    - P32A0 
    - USB_PHY_RST_N 
  * - XD50 
    - P32A1 
    - CODEC_RST_N 
  * - XD51 
    - P32A2 
    - MCLK_SEL 
  * - XD52 
    - P32A3 
    - LED_A
  * - XD53 
    - P32A4 
    - LED_B

Clocking
++++++++

The board has two on-board oscillators for master clock generation.
These produce 11.2896MHz for sample rates 44.1, 88.2, 176.4KHz etc and
24.567MHz for sample rates 48, 96, 192kHz etc. 

The required master clock is selected from one of these using an external mux circuit via 
port *P32A[2]* (pin 2 of port 32A). Setting *P32A[2]* high 
selects 11.2896MHz, low selects 24.576MHz.

.. only:: latex

 .. figure:: images/clocks.pdf

   Audio Clock Connections

.. only:: html

 .. figure:: images/clocks.png

   Audio Clock Connections

The reference design board uses a 24 bit, 192kHz stereo audio CODEC 
(Cirrus Logic CS4270).

The CODEC is configured to operate in *stand-alone mode* meaning that no
serial configuration interface is required.  The digital audio interface
is set to I2S mode with all clocks being inputs (i.e. slave mode).

The CODEC has three internal modes depending on the sampling rate used. 
These change the oversampling ratio used internally in the CODEC. The 
three modes are shown below:

.. list-table:: CODEC Modes
  :header-rows: 1
  :widths: 30 25

  * - CODEC mode    
    - CODEC sample rate range (kHz)
  * - Single-Speed 
    - 4-54
  * - Double-Speed
    - 50-108
  * - Quad-Speed 
    - 100-216

In stand-alone mode, the CODEC automatically determines which mode to operate in
based on input clock rates.

The internal master clock dividers are set using the MDIV pins.  MDIV is tied low
and MDIV2 is connected to bit 2 of port 32A (as well as to the master clock 
select).
With MDIV2 low, the master clock must be 256Fs in single-speed mode, 128Fs in 
double-speed mode and 64Fs in quad-speed mode. This allows an 11.2896MHz master 
clock to be used for sample rates of 44.1, 88.2 and 176.4kHz.

With MDIV2 high, the master clock must be 512Fs in single-speed mode, 256Fs in 
double-speed mode and 128Fs in quad-speed mode. This allows a 24.576MHz master 
clock to be used for sample rates of 48, 96 and 192kHz.

When changing sample frequency, the
:c:func:`CodecConfig` function first puts the CODEC into reset by
setting *P32A[1]* low. It selects the required master clock/CODEC dividers and
keeps the CODEC in reset for 1ms to allow the clocks to stabilize.
The CODEC is brought out of reset by setting *P32A[1]* back high.


.. port32A

HID
+++

The reference design implements basic HID controls.  The call to ``vendor_ReadHidButtons()`` simply
reads from buttons A and B and returns their state in the relevant bits depending on the desired
functionality (play/pause/skip etc).  Note the buttons are active low, the HID controls active high.  
The buttons are therefore read and then inverted.

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/vendorhid.xc
   :start-after: #ifdef HID_CONTROLS
   :end-before: #endif //

In the example above the buttons are assigned to volume up/down.

Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
build options.  These are described in :ref:`usb_audio_sec_custom_defines_api`. 

The design has only been fully validated against the build options as set in the
application as distributed.  See :ref:`usb_audio_sec_valbuild` for details and binary naming.

In practise, due to the similarities between the U-Series and L-Series feature set, it is fully expected that all listed U-Series
configurations will operate as expected on the L-Series and vice versa.

Configuration 2ioxs
~~~~~~~~~~~~~~~~~~~

This configuration runs in high-speed Audio Class 2.0 mode, has the mixer disabled, supports 2 channels in, 2
channels out and supports sample rates up to 192kHz and S/PDIF transmit.

Configuration 2iomx
~~~~~~~~~~~~~~~~~~~

This configuration disables S/PDIF and enables MIDI.

This configuration can be achieved by in the Makefile by defining ``SPDIF`` as zero::
    
    -DSPDIF=0

and ``MIDI`` as 1::

    -DMIDI=1

Configuration 1ioxs
~~~~~~~~~~~~~~~~~~~~

This configuration is similar to the first configuration apart from it runs in Audio 1.0 over full-speed USB.

This is achieved in the Makefile by::

    -DAUDIO_CLASS=1



