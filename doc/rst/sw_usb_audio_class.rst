USB Audio Class Version Support
-------------------------------

The XMOS USB Audio framework supports both USB Audio Class 1.0 and Audio Class 2.0.

USB Audio Class 2.0 offers many improvements over USB Audio Class 1.0, most notable is the complete support for high-speed operation.  This means that Audio Class devices are no longer limited to full-speed operation allowing greater channel counts, sample frequencies and sample bit-depths. Additional improvement, amoungst others, include: 

- Added support for multiple clock domains, clock description and clock control

- Extensive support for interrupts to inform the host about dynamic changes that occur to different entities such as Clocks etc

Driver Support
~~~~~~~~~~~~~~

Audio Class 1.0 
+++++++++++++++

Audio Class 1.0 is fully supported in Apple OSX.  Audio Class 1.0 is fully supported in all modern Microsoft Windows operating systems (i.e. Windows XP and later). 

Audio Class 2.0
+++++++++++++++

Audio Class 2.0 is fully supported in Apple OSX since version 10.6.4.  Audio Class 2.0 is not supported natively by Windows operating systems. It is therefore required that a driver is installed.  Documentation of Windows drivers is beyond the scope of this document, please contact XMOS for further details.

Audio Class 1.0 Mode and Fall-back
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The normal default for XMOS USB Audio applications is to run as a high-speed Audio Class 2.0
device. However, some products may prefer to run in Audio Class 1.0 mode, this is normally to 
allow "driver-less" operation with Windows operating systems. 

.. note::

    To ensure specification compliance, Audio Class 1.0 mode *always* operates at full-speed USB. 

The device will operate in full-speed Audio Class 1.0 mode if one of the following is true:

-  The code is compiled for USB Audio Class 1.0 only.

-  The code is compiled for USB Audio Class 2.0 and it is connected
   to the host over a full speed link (and the Audio Class fall back is 
   enabled).

The options to control this behavior are detailed in :ref:`usb_audio_sec_custom_defines_api`. 

When running in Audio Class 1.0 mode the following restrictions are applied:

- MIDI is disabled.

- DFU is disabled (Since Windows operating systems would prompt for a DFU driver to be installed)

Due to bandwidth limitations of full-speed USB the following sample-frequency restrictions are also applied:

-  Sample rate is limited to a maximum of 48kHz if both input and output are enabled.

-  Sample rate is limited to a maximum of 96kHz if only input *or* output is enabled.

