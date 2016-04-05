.. _usb_audio_sec_hw_216_mc:


xCORE-200 Multi-Channel Audio Board
-----------------------------------

`The XMOS xCORE-200 Multi-channel Audio board <https://www.xmos.com/support/boards?product=18334>`_ 
(XK-AUDIO-216-MC) is a complete hardware and reference software platform targeted at up to 32-channel USB and networked audio applications, such as DJ decks and mixers.

The Multichannel Audio Platform hardware is based around the XE216-512-TQ128 multicore microcontroller; an dual-tile xCORE-200 device with an integrated High Speed USB 2.0 PHY, RGMII (Gigabit Ethernet) interface and 16 logical cores delivering up to 2000MIPS of deterministic and responsive processing power.

Exploiting the flexible programmability of the xCORE-200 architecture, the Multi-channel Audio Platform supports either USB or network audio source, streaming 8 analogue input and 8 analogue output audio channels simultaneously - at up to 192kHz. Ideal for mixing two sources and providing main and headphone monitor output feeds.

For full details regarding the hardware please refer to `xCORE-200 Multichannel Audio Platform Hardware Manual <https://www.xmos.com/support/boards?product=18334&component=18687>`_.

The reference board has an associated firmware application that uses the USB Audio 2.0 software reference
platform. Details of this application can be found in section :ref:`usb_audio_sec_216_audio_sw`.

Analogue Input & Output
+++++++++++++++++++++++

A total of eight single-ended analog input channels are provided via 3.5mm stereo jacks. Each is fed into a CirrusLogic CS5368 ADC.
Similarly a total of eight single-ended analog output channels are provided. Each is fed into a CirrusLogic CS4384 DAC.

The four digital I2S/TDM input and output channels are mapped to the xCORE input/outputs through a header array. The jumper allows channel selection when the ADC/DAC is used in TDM mode

Digital Input & Output
++++++++++++++++++++++

Optical and coaxial digital audio transmitters are used to provide digital audio input output in formats such as IEC60958 consumer mode (S/PDIF) and ADAT.
The output data streams from the xCORE-200 are re-clocked using the external master clock to synchronise the data into the audio clock domain. This is achieved using simple external D-type flip-flops.

MIDI
++++

MIDI I/O is provided on the board via a standard Gameport connector. The signals are buffered using 5V line drivers and are then connected to 1-bit ports on the xCORE-200, via a 5V to 3.3V buffer.

Audio Clocking
++++++++++++++

A flexible clocking scheme is provided for both audio and other system services. In order to accommodate a multitude of clocking options, the low-jitter master clock is generated locally using a frequency multiplier PLL chip. The chip used is a Phaselink PL611-01, which is pre-programmed to provide a 24MHz clock from its CLK0 output, and either 24.576 MHz or 22.5792MHz from its CLK1 output.

The 24MHz fixed output is provided to the xCORE-200 device, as the main processor clock. It also provides the reference clock to a Cirrus Logic CS2100, which provides a very low jitter audio clock from a synchronisation signal provided from the xCORE-200.

Either the locally generated clock (from the PL611) or the recovered low jitter clock (from the CS2100) may be selected to clock the audio stages; the xCORE-200, the ADC/DAC and Digital output stages.

LEDs, Buttons and Other IO
++++++++++++++++++++++++++

An array of 4*4 green LEDs, 3 buttons and a switch are provided for general purpose user interfacing. The LED array is driven by eight signals each controlling one of 4 rows and 4 columns.

A standard XMOS xSYS interface is provided to allow host debug of the board via JTAG.



|newpage|



