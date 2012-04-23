.. _usb_audio_interface_sg_sw:

The USB Audio 2.0 Application 
-----------------------------

The USB Audio 2.0 Application is an application of the USB audio
framework specifically for the hardware described in Section
:ref:`usb_audio_interface_sg_hw` and is implemented on the XS1-L1 single core
device (500MIPS).
The software design supports two channels of audio (input and output) at sample frequencies up to
192kHz. It supports iOS devices by identifying and authenticating over USB. It
automatically selects between PC and iOS host based on the the presense of an iOS device.

It uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * MIDI
 * iOS

The following diagrams show the software layout of the code
running on the XS1-L1 chip. Most units run in a single
thread concurrently with the others units. The lines show the
communication between each functional unit. Due to the MIPS
requirement of the USB driver, only six threads can be
run on the single core L1 device.

.. only:: latex

  .. _fig_threads-midi:

  .. figure:: images/threads-midi-crop-ios.pdf
     :figwidth: 60%
     :align: center

     L1 Software Thread Diagram (with MIDI I/O)

.. only:: html

  .. figure:: images/threads-midi-crop-ios.png

     L1 Software Thread Diagram (with MIDI I/O)   

.. only:: latex

  .. _fig_threads:

  .. figure:: images/threads-crop-ios.pdf
     :figwidth: 60%
     :align: center

     L1 Software Thread Diagram (without MIDI I/O)

.. only:: html

  .. figure:: images/threads-crop-ios.png

     L1 Software Thread Diagram (without MIDI I/O)   


Port 32A IO expander
++++++++++++++++++++

Port 32A on the XS1-L1 is a 32-bit wide port. 4 pins of this are used to control a pair of shift registers for IO expansion.

Please see `Shift Register Expansion of XS1 Devices <http://www.xmos.com/published/shift-register-expansion-xs1-devices>`_ for an explanation of the hardware.

The XUAI development kit provides higher level access to port32A via ``port32A_set``, ``port32A_unset`` and ``port32A_mask_and_set`` functions. These may be accessed safely by multiple threads as a lock is used to protect access. If all access to these signals is via these then it will remain possible to select between using the shift register and port32A directly using the IO_EXPANSION macro. 

The following tables show the signals connected to the input and output shift register on port 32A on the XUAI board.

.. list-table:: Port 32A output shift register Signals
  :header-rows: 1
  :widths: 30 30

  * - Pin
    - Signal
  * - 0 
    - MIDI_EN_N
  * - 1 
    - LED_B
  * - 2 
    - LED_A
  * - 3 
    - USB_PHY_RST_N 
  * - 4 
    - ACC_DET_ID_EN 
  * - 5 
    - USB_SEL 
  * - 6 
    - MCLK_SEL 
  * - 7 
    - CODEC_RST_N 

.. list-table:: Port 32A input shift register Signals
  :header-rows: 1
  :widths: 30 30

  * - Pin
    - Signal
  * - 0 
    - SW1
  * - 1 
    - SW2
  * - 2 
    - 30PIN_DEV_DETECT 

Power
+++++

The XUAI development kit must be self powered rather than bus powered.

Validated Build Options
+++++++++++++++++++++++

The software can be built in several ways by changing the
option described in :ref:`sec_custom_defines_api`. However, the design
has only been validated against the build options as set in the
application as distributed with the following two variations.

SPDIF is not supported at present due to resource limitations.

Configuration 1 (default)
~~~~~~~~~~~~~~~~~~~~~~~~~

This configuration has MIDI and IOS enabled, supports 2 channels in, 2
channels out, supports sample rates up to 192kHz and DFU.

This configuration is achieved with the following
in ``customdefines.h``::

#define MIDI          1
#define IAP           1

Configuration 2
~~~~~~~~~~~~~~~

Compared to configuration 1, this configuration disables MIDI.

This configuration can be achieved with the following
in ``customdefines.h``::

#define MIDI          0
#define IAP           1
