XMOS xCORE-200 USB Audio
========================

Overview
........

The firmware provides a high-speed USB Audio device designed to be compliant to version 2.0 of the USB Audio Class Specification based on the XMOS U16 device.

Key Features
............

The app_usb_aud_xk_216_mc application is designed to run on the xCORE 200 MC Audio Board in. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 4 channels analogue input and 4 channels analogue output (Via I2S to 2 x Stereo CODECs)

- S/PDIF output (via COAX connector)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- MIDI input and output

Build configurations
....................

A reduced set of build configurations will be tested in alpha and beta releases. Some configurations may be hidden behind the FULL build flag to indicate their limited testing. For example (illustration only)::

  $ xmake allconfigs
  hifi i2s_slave tdm

and::

  $ xmake allconfigs FULL=1
  1i2o2xxxxxx 1i8o2xxxxxx 2i0o8xxxxx_tdm8_slave 2i10o10msxxxx 2i10o10xssxxx
  2i10o10xsxxxd 2i10o10xsxxxx 2i10o10xsxxxx_mix8 2i10o10xxxxxd 2i10o10xxxxxx
  2i10o10xxxxxx_slave 2i10o16xxxaxx 2i16o16xxxaax 2i16o16xxxxx_tdm8
  2i32o32xsxxx_tdm8 2i32o32xxxxx_tdm8 2i8o8xxxxx_tdm8 2i8o8xxxxx_tdm8_slave
  hifi i2s_slave tdm

Known Issues
............

- On occasion with the legacy build configuration 2i8o8xxxxx_tdm8_slave (or any configuration where the Cirrus CS5368 ADC is used as clock master and the Cirrus CS4364 DAC slaves to this clock) sample-rate changes can cause a channel swapping issue in the Cirrus DAC. This incompatibility is documented in Cirrus note AN302 (https://www.cirrus.com/en/pubs/appNote/AN302REV1.pdf) 

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support
