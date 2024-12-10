.. _usb_audio_hardware_platforms:

****************************
USB Audio hardware platforms
****************************

This section describes the hardware development platforms supported by the `XMOS` USB Audio
reference design software.

+--------------------+---------------------+--------------------+---------------------+
| Board              | `xcore` device      | Analog channels    | Digital Rx/Tx & MIDI|
+====================+=====================+====================+=====================+
|XK_EVK_XU316        |    `xcore.ai`       |  2 in + 2 out      |        N/A          |
+--------------------+---------------------+--------------------+---------------------+
|XK_AUDIO_316_MC_AB  |    `xcore.ai`       |  8 in + 8 out      |       Supported     |
+--------------------+---------------------+--------------------+---------------------+
|XK_AUDIO_216_MC_AB  |    `xcore-200`      |  8 in + 8 out      |       Supported     |
+--------------------+---------------------+--------------------+---------------------+

Each of the platforms supported has a Board Support Package (BSP), the code for which can be be
found in `lib_board_support <https://www.xmos.com/file/lib_board_support>`_.
The code in ``lib_board_support`` abstracts away all of the hardware setup including enabling
external hardware blocks and DAC and ADC configuration and provides a translation
layer from the common API supported by `lib_xua <https://www.xmos.com/file/lib_xua>`_ for
initialising and configuring hardware on a sample rate or stream format change.

Detailed feature sets for the each of the supported boards can be found in the documentation for
`lib_board_support <https://www.xmos.com/file/lib_board_support>`_.

