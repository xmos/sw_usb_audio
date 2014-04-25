.. _usb_audio_sec_l2_audio_sw:

USB Audio 2.0  Multichannel Reference Design (L-Series) Application
-------------------------------------------------------------------

The USB Audio 2.0 Multichannel Reference Design is an application of the USB audio
framework specifically for the hardware described in :ref:`usb_audio_sec_l2_audio_hw` and is
implemented on an L-Series dual tile device (1000MIPS).  The code can be found in
`app_usb_aud_l2`

The software design supports up to 16 channels of audio in and 10 channels of audio out and
supports sample frequencies up to 192 kHz and uses the following components:

 * XMOS USB Device Driver (XUD)
 * Endpoint 0
 * Endpoint buffer
 * Decoupler
 * Audio Driver
 * Device Firmware Upgrade (DFU)
 * Mixer
 * S/PDIF Transmitter
 * S/PDIF Receiver
 * ADAT Receiver
 * Clockgen
 * MIDI

:ref:`usb_audio_l2_threads`  shows the software layout of the USB
Audio 2.0 Multichannel Reference Design.

.. _usb_audio_l2_threads:

.. figure:: images/threads-l2-crop.*
     :width: 90%
     :align: center    

     Dual Tile L-Series Reference Design Core Layout


Clocking
++++++++

For complete clocking flexibility the dual tile L-Series reference design drives a reference clock to an external fractional-n clock multiplier IC (Cirrus 
Logic CS2300).  This in turn generates the master clock used over the 
design.  This is described in :ref:`usb_audio_sec_clock_recovery`.


Validated Build Options
+++++++++++++++++++++++

The reference design can be built in several ways by changing the
option described in :ref:`usb_audio_sec_custom_defines_api`. However, the design
has only been validated against the build options as set in the
application as distributed with the following four variations.

Configuration 1
~~~~~~~~~~~~~~~

All the #defines are set as per the distributed
application. It has the mixer enabled, supports 16 channels in, 10
channels out and supports sample rates up to 96kHz.

Configuration 2
~~~~~~~~~~~~~~~

The same as Configuration 1 but with the CODEC
set as I2S master (and the XCORE Tile as slave).

This configuration can be achieved by commenting out the following
line in ``customdefines.h``::

  //#define CODEC_SLAVE        1    

Configuration 3
~~~~~~~~~~~~~~~

This configuration supports sample rates up to 192kHz but only
supports 10 channels in and out. It also disables
ADAT receive and the mixer. It can be achieved by commenting out  
the following lines in ``customdefines.h``::

  //#define MIXER
  //#define ADAT_RX            1

and changing the following defines to::

  #define NUM_USB_CHAN_IN  (10)   
  #define I2S_CHANS_ADC    (6)
  #define SPDIF_RX_INDEX   (8)

Configuration 4
~~~~~~~~~~~~~~~

The same as Configuration 3 but with the CODEC set as I2S master. 
This configuration can be made by making the changes for Configuration
3 and commenting out the following line in ``customdefines.h``::

 //#define CODEC_SLAVE        1    


