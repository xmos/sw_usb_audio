Multi-rate I2S Example
======================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xcore.ai multi-channel USB audio board with multiple I2S buses
:keywords: USB, UAC, I2S, SRC
:boards: XK-AUDIO-316-MC (rev 1.1)

Overview
........

As supplied, the XMOS reference design software only supports as single I2S bus. This example shows
how a secondary I2S bus can be added to the design that runs at a different (lower) rate.

This secondary I2S bus is implemented by running an instance of lib_i2s. To allow this bus to run
at a different rate; Synchronous Sample Rate Conversion (SSRC) is used, as supplied by lib_src.

The frequency of this secondary I2S bus is derived from the same master clock as the primary I2S
bus and so synchronous rate conversion can be used (rather than asynchronous rate conversion). In
the case of this example the master clock is generated from application PLL built-in to the
xcore.ai device.

If the two clocks are not related, this example is not suitable, the two clocks will drift leading
to artifacts in the audio stream.

The XK-316-AUDIO-MC board only supports a singles I2S bus. The secondary I2S bus can be evaluated
on the XK-AUDIO-316-MC board by using jumper wires to connect an external DAC. By default, these
should be connected to the following I/O:

- External DAC BCLK to DAC_D2 (J7)
- External DAC LRCLK to DAC_D3 (J7)
- External DAC DATA to DAC_D1 (J7)
- External DAC MCLK to MCLK (J7)

Note, these I/O are also used for data to DACs 1, 2, and 3. Consequently the analogue output from
the XK-AUDIO-315-MC is limited to analogue stereo output, via the primary I2S bus, to DAC 0.

Key Features
............

The app_usb_aud_xk_316_mc_multirate_i2s application is designed to run on the XK-316-AUDIO-MC board.
It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input and 2 channels analogue output (Via I2S to 1 x Stereo CODECs)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- 2 additional output channels via an secondary I2S bus

Known Issues
............

- Dynamic sample rate change is not currently supported. The USB audio device and primary I2S bus
  are currently set to a fixed rate of 192kHz. The secondary I2S bus is set to a fixed rate of
  48kHz.

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


