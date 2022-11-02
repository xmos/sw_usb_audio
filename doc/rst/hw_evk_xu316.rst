xCORE.ai Evaluation Kit
.......................

The `XMOS xCORE.ai Evaluation Kit` (XK-EVK-XU316) is an evaluation board for the xCORE.ai multi-core microcontroller 
from `XMOS`.

.. _hw_evk_xu316_image:
.. figure:: images/xk_evk_xu316.*
    :scale: 50%
    :align: center

    xCORE.ai Evaluation Kit

The XK-EVK-XU316  allows testing in multiple application scenarios and provides a good general software development
board for simple tests and demos. The XK-EVK-XU316 comprises an `xCORE.ai` processor with a set of I/O devices and 
connectors arranged around it, as shown in ::ref:`hw_evk_xu316_block_diagram`. 

.. _hw_evk_xu316_block_diagram:
.. figure:: images/xk_evk_xu316_block_diagram.*
    :scale: 70%
    :align: center

    xCORE.ai Evaluation Kit block diagram

External hardware features board include, four general purpose LEDs, two general purpose push-button switches, 
a PDM microphone connector, audio codec with line-in and line-out jack, QSPI flash memory, LPDDR1 external memory 
58 GPIO connections from tile 0 and 1, micro USB for power and host connection, MIPI connector for a MIPI camera, 
integrated `xTAG` debug adapter and a reset switch with LED to indicate running. 

For full details regarding the hardware please refer to `XK-EVK-XU316 xCORE.ai Evaluation Kit Manual
<https://www.xmos.ai/download/xcore.ai-explorer-board-v2.0-hardware-manual(5).pdf>`_.

The XK-EVK-XU316 hardware has an associated firmware application that uses ``lib_xua`` to implement an example USB 
Audio device. Full details of this application can be found later in this document.

.. warning:: 

    The `xCORE.ai Evaluation Kit` is a general purpose evaluation platform and should be considered as an example rather
    than a fully fledged reference design.

Analogue Audio Input & Output
+++++++++++++++++++++++++++++

A stereo CODEC (TLV320AIC3204), connected to the xCORE.ai device via an I2S interface, provides analogue input/output 
functionality at line level.

The audio CODEC is are configured by the `xCORE.ai` device via an I2C bus. 

Audio Clocking
++++++++++++++

`xCORE.ai` devices are equipped with a secondary (or `application`) PLL which is used to generate the audio clocks for the CODEC.

LEDs, Buttons and Other IO
++++++++++++++++++++++++++

Four green LED's and two push buttons are provided for general purpose user interfacing. 

The LEDs are connected to PORT 4C and the buttons are connected to bits [0:1] of PORT 4D.

All spare I/O is brought out and made available on 0.1" headers for easy connection of expansion 
boards etc.

Power
+++++

The XK-EVK-XU316 requires a 5V power source that is normally provided through the micro-USB cable J3.
The voltage is converted by on-board regulators to the 0V9, 1V8 and 3V3 supplies used by the components.

The board should therefore be configured to present itself as a bus powered device when connected to an 
active USB host.

Debug
+++++

For convenience the board includes an on-board xTAG4 for debugging via JTAG/xSCOPE. 
This is accessed via the USB (micro-B) receptacle marked ``DEBUG``. 

