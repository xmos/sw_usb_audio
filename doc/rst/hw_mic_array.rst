:orphan:

.. _usb_audio_sec_hw_mic_arr:


xCORE-200 Microphone Array Board
--------------------------------

`The XMOS xCORE-200 Microphone Array board <https://www.xmos.com/support/boards?product=20258>`_
(XK-USB-MIC-UF216) is design available from XMOS based on a dual-tile XMOS xCORE-200 device.

The board integrates the following building blocks: multiple omni-directional microphones,
on-board low-jitter clock sources, configurable user input buttons and a USB for connectivity.
These features make it an ideal platform for a range of multichannel microphone aggregation products.

The board is powered by an XUF216-512 xCORE-200 multicore microcontroller. This device has sixteen
32bit logical cores that deliver up to 2000MIPS completely deterministically. In addition the
XUF216 has powerful DSP properties with native 32bit/64 instructions delivering up to 1000MMACS.

:ref:`usb_audio_mic_hw_diagram` shows the block layout of the xCORE-200 Microhone Array board.

.. _usb_audio_mic_hw_diagram:

.. figure:: images/hw_mic_block.*
     :align: center
     :width: 100%

     xCORE-200 Microphone Array Board Block Diagram

For full details regarding the hardware please refer to `xCORE Microphone Array Hardware Manual <https://www.xmos.com/download/private/xCORE-Microphone-Array-Hardware-Manual%281v1%29.pdf>`_.

The reference board has an associated firmware application that uses the USB Audio 2.0 software reference
platform. Details of this application can be found in section :ref:`usb_audio_sec_mic_arr_audio_sw`.

Microphones
+++++++++++

The xCORE Microphone Array board features 7 MEMS microphones with PDM (Pulse Density Modulation) output.

:ref:`usb_audio_mic_hw_mics_diagram` shows the microphone arrangement on the board.

.. _usb_audio_mic_hw_mics_diagram:

.. figure:: images/hw_mic_mics.*
     :align: center
     :width: 100%

     xCORE-200 Microphone Array Board Microphone Arrangement

Analogue Output
+++++++++++++++

As well at 7 PDM microphones the board also provides a stereo DAC (CS43L21) with an integrated headphone
amplifier. The CS43L21 is connected to the xCORE-200 through an I2S interface and is configured using an I2C interface.

Audio Clocking
++++++++++++++

The board provides a low-jitter clock-source, an 24.576MHz oscillator, to serve as reference clock
to the CS2100-CP (Cirrus Logic) Fractional-N PLL (U22).

The CS2100 generates a low-jitter output signal that is distributed to the xCORE- 200 device and DAC.
The CS2100 device is configured using the I2C interface.

Buttons, LEDs and Other IO
++++++++++++++++++++++++++

The board has 13 LEDs that are controlled by the xCORE-200 GPIO. The layout of the LEDs is shown in :ref:`usb_audio_mic_hw_leds_diagram`.

.. _usb_audio_mic_hw_leds_diagram:

.. figure:: images/hw_mic_leds.*
     :align: center
     :width: 95%

     xCORE-200 Microphone Array Board LED Arrangement


LED 0 to LED 11 (D2-D13) are positioned around the edge of the board, one each side of every microphone.
LED 12 (D14) is positioned next to the middle microphone.

A green LED (PGOOD) by the USB connector indicates a 3V3 power good signal.

Four general purpose push-button switches are provided. When pressed, each button creates a connection from the I/O to GND.

A standard XMOS xSYS interface (J2) is provided to allow host debug of the board via JTAG.

The board also includes Ethernet connectivity, however, this is outside the scope of this documentation.

|newpage|



