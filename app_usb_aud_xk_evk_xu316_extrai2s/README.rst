XMOS xcore.ai USB Audio
=======================

:maintainer: Ross Owen
:scope: Example
:description: USB Audio application for xCORE.ai eXplorer board
:keywords: USB, UAC, I2S
:boards: xCORE.ai eXplorer (rev 1.x)

Overview
........

As supplied the XMOS reference design software only supports I2S lines on one tile. However, when trying to fit large numbers of I2S channels into a small pin-count device it may be desirable to use I/O on multiple tiles for I2S.  This can be achieved by running an extra I2S slave core and hardware loop backs for LRCLK and BCLK lines (assuming xCORE is I2S master in the system).

This example shows how an extra I2S slave core can be integrated into the USB Audio Reference Design.

The provided software example adds an additional two I2S input channels.  These can be demonstrated/tested on the xCORE.ai Explorer Board by using external jumper wires to connect the ADC output of the CODEC to the newly added extra I2S I/O as follows:

- BCLK to X1D38 (J10)
- LRCLK to X1D39 (J16)
- ADC_DAT to X1D36 (J10)

Note, for correct operation external jumper cables must be attached between the following pins (required for 1v0 hardware only):

- MCLK to X0D11 (J14)

Key Features
............

The app_usb_aud_xk_evk_xu316 application is designed to run on the xCORE.ai eXplorer board. It uses the XMOS USB Audio framework to implement a USB Audio device with the following key features:

- USB Audio Class 2.0 Compliant

- Fully Asynchronous operation

- 2 channels analogue input and 2 channels analogue output (Via I2S to 1 x Stereo CODECs)

- Supports for the following sample frequencies: 44.1, 48, 88.2, 96, 176.4, 192kHz

- 2 extra I2S input channels via additional I2S slave core

Known Issues
............

- None.

See README in sw_usb_audio for general issues.

Support
.......

For all support issues please visit http://www.xmos.com/support


