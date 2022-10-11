xCORE.ai Multi-Channel Audio Board
...................................

The `XMOS xCORE.ai Multichannel Audio Board` (XK-AUDIO-316-MC) is a complete hardware and software reference platform targeted at up to 32-channel USB audio applications, such as DJ decks, mixers and other musical instrument interfaces.  The board can also be used to prototype products with reduced feature sets or HiFi style products.

The XK-AUDIO-316-MC is based around the XU316-1024-TQ128-C24 multicore microcontroller; a dual-tile xCORE.ai device with an integrated High Speed USB 2.0 PHY and 16 logical cores delivering up to 2400MIPS of deterministic and responsive processing power.

Exploiting the flexible programmability of the xCORE.ai architecture, the XK-AUDIO-316-MC supports a USB audio source, streaming 8 analogue input and 8 analogue output audio channels simultaneously - at up to 192kHz. It also supports digital input/output streams (S/PDIF and ADAT) and MIDI. Ideal for consumer and professional USB audio interfaces. The board can also be used for testing general purpose audio DSP activities - mixing, filtering, etc.

The guaranteed Hardware-ResponseTM times of xCORE technology always ensure lowest latency (round trip as low as 3ms), bit perfect audio streaming to and from the USB host

For full details regarding the hardware please refer to `xCORE.ai Multichannel Audio Platform Hardware Manual <ADD LINK HERE>`_.

The XK-AUDIO-316-MC reference hardware has an associated firmware application that uses `lib_xua` to implement fully-featured and production ready USB Audio solution. Full details of this application can be found later in this document.

|newpage|

Hardware Features
+++++++++++++++++

The location of the various featurs of the xCORE.ai Multichannel Audio Board (XK-AUDIO-316-MC) is shown in :ref:`xk_audio_316_mc_block_diagram`. 

.. _xk_audio_316_mc_block_diagram:
.. figure:: images/xk_316_audio_mc.pdf
    :scale: 70%

    xCORE.ai Multichannel Audio Board block diagram

It includes the following features:

- A: xCORE.ai (XU316-1024-TQ128-C24) multicore microcontroller device

- B: 8 line level analog outputs (3.5mm stereo jacks)

- C: 8 line level analog inputs (3.5mm stereo jacks)

- D: 384kHz 24 bit audio DACs

- E: 192kHz 24 bit audio ADCs

- F: Optical connections for digital interface (e.g. S/PDIF and ADAT)

- G: Coaxial connections for digital interfaces (e.g. S/PDIF)

- H: MIDI in and out connections

- I: Flexible audio master clock generation

- J: USB 2.0 micro-B jacks

- L: 4 general purpose LEDs

- M: 3 general purpose buttons

- O: Flexible I2S/TDM input data routing

- P: Flexible I2S/TDM output data routing

- Q: Integrated power supply

- R: Quad-SPI boot ROM

- S: 24MHz Crystal

- T: Integrated XTAG4 debugger


Analogue Input & Output
+++++++++++++++++++++++

A total of eight single-ended analog input channels are provided via 3.5mm stereo jacks. These inputs feed into a pair of quad-channel PCM1865 ADCs from Texas Instruments.

A total of eight single-ended analog output channels are provided. These are fed from four PCM5122 stereo DAC's from Texas instruments.

All ADC's and DAC's are configured via an I2C bus. Due to an clash of device addresses a I2C mux is used.

The four digital I2S/TDM input and output channels are mapped to the xCORE input/outputs through a header array. These jumpers allow channel selection when the ADCs/DACs are used in TDM mode.

Digital Input & Output
++++++++++++++++++++++

Optical and coaxial digital audio transmitters are used to provide digital audio input output in formats such as IEC60958 consumer mode (S/PDIF) and ADAT.
The output data streams from the xCORE are re-clocked using the external master clock to synchronise the data into the audio clock domain. This is achieved using simple external D-type flip-flops.

MIDI
++++

MIDI input and output is provided on the board via standard 5-pin DIN connectors compliant to the MIDI specification.
The signals are buffered using 5V line drivers and are then connected ports on the xCORE, via a 5V to 3.3V buffer. 
A 1-bit port is used for receive and a 4-bit port is used for transmit. A pullup resistor on the MIDI output ensures there
is no MIDI output when the xCORE device is not actively driving the output.

Audio Clocking
++++++++++++++

In order to accommodate a multitude of clocking options a flexible clocking scheme is provided for the audio subsystem.

Three methods of generating an audio master clock are provided on the board:

    * A Cirrus Logic CS2100-CP PLL device.  The CS2100 features both a clock generator and clock multiplier/jitter reduced clock frequency synthesizer (clean up) and can generate a low jitter audio clock based on a synchronisation signal provided by the xCORE

    * A Skyworks Si5351B PLL device. The Si5351 is an I2C configurable clock generator that is suited for replacing crystals, crystal oscillators, VCXOs, phase-locked loops (PLLs), and fanout buffers.

    * xCORE.ai devices are equipped with a secondary (or `application`) PLL which can be used to generate audio clocks.

Selecting between these methods is done via writing to bits 6 and 7 of PORT 8D on tile[0]. See :ref:`hw_316_ctrlport`.

.. note::
    
    The supplied software currently supports the xCORE.ai secondary PLL or CS2100 device.

.. _hw_316_ctrlport:

Control I/O
+++++++++++

4 bits of PORT 8C are used to control external hardware on the board. This is described in :ref:`table_316_ctrlport`.

.. _table_316_ctrlport:

.. table:: PORT 8C functionality
    :class: horizontal-borders vertical_borders

    +--------+-----------------------------------------+------------+------------+
    | Bit(s) | Functionality                           |    0       |     1      |
    +========+=========================================+============+============+
    | [0:3]  | Unused                                  |            |            |
    +--------+-----------------------------------------+------------+------------+
    | 4      | Enable 3v3 power for digital (inverted) |  Enabled   |  Disabled  |
    +--------+-----------------------------------------+------------+------------+
    | 5      | Enable 3v3 power for analogue           |  Disabled  |  Enabled   |
    +--------+-----------------------------------------+------------+------------+
    | 6      | PLL Select                              |   CS2100   |   Si5351B  |
    +--------+-----------------------------------------+------------+------------+
    | 7      | Master clock direction                  |   Output   |   Input    |
    +--------+-----------------------------------------+------------+------------+


.. note::
     
    To use the xCORE application PLL bit 7 should be set to 0. To use one of the external PLL's bit 7 should be set to 1. 


LEDs, Buttons and Other IO
++++++++++++++++++++++++++

All programmable I/O on the board is configured for 3.3 volts.

Four green LED's and three push buttons are provided for general purpose user interfacing. 

The LEDs are connected to PORT 4F and the buttons are connected to bits [0:2] of PORT 4E, both on tile 0. Bit 3 of this
port is connected to the (currently unused) ADC interrupt line.

The board also includes support for an AES11 format Word Clock input via 75 ohm BNC. The software does not currently 
support any functionality related to this and it is provided for future expansion.

All spare I/O is brought out and made available on 0.1" headers for easy connection of expansion 
boards etc.

Power
+++++

The board is capable of acting as a USB2.0 self or bus powered device. If bus powered, the board takes
power from the ``USB DEVICE`` connector (micro-B receptacle). If self powered, board takes power 
from ``EXTERNAL POWER`` input (micro-B receptacle).

A Power Source Select (marked ``PWR SRC``) is used to select between bus and self-powered configuration. 

.. note::

    To remain USB compliant the software should be properly configured for bus vs self powered operation

Debug
+++++

For convenience the board includes an on-board xTAG4 for debugging via JTAG/xSCOPE. 
This is accessed via the USB (micro-B) receptacle marked ``DEBUG``. 

