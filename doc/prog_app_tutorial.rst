A USB Audio Application
-----------------------
.. highlight:: none

This section provides a walk through of the single tile USB Audio Reference Design (L-Series) 
example, which can be found in the ``app_usb_aud_l1`` directory. 

In each application directory the ``src`` directory is arranged into two folders:

#. An ``core`` directory containing source items that must be made available to the USB Audio
framework

#. An ``extensions`` directory that includes extensions to the framework such as CODEC config etc

The ``core`` folder for each application contains:

#. A ``.xn`` file to describe the hardware platform the app will run on
#. A custom defines file: ``customdefines.h`` for framework configuration

Custom Defines
~~~~~~~~~~~~~~

The ``customdefines.h`` file contains all the #defines required to tailor the USB audio framework
to the particular application at hand.  Typically these over-ride default values in `devicedefines.h`
in `module_usb_audio`.


First there are defines to determine overall capability. For this appliction 
S/PDIF output and DFU are enabled. Note that `ifndef` is used to check that the option is not
already defined in the makefile.

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: in Makefile */
  :end-before: /* Audio Class Version 

Next, the file defines the audio properties of the application. This application has stereo in and
stereo out with an S/PDIF output that duplicates analogue channels 1 and 2 (note channels are 
indexed from 0):

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: /* Defines relating to channel 
  :end-before: /* Master clock defines

The file then sets some defines for the master clocks on the hardware and the maximum sample-rate
for the device. 

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: SPDIF_TX_INDEX     (0)
  :end-before: /***** Defines relating to USB 

Finally, there are some general USB identification defines to be
set. These are set for the XMOS reference design but vary per
manufacturer:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: //:usb_defs
  :end-before: //:

For a full description of all the defines that can be set in
``customdefines.h`` see :ref:`sec_custom_defines_api` 

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~

In addition to the custom defines file, the application needs to provide implementations of user 
functions that are specific to the application.

For `app_usb_aud_l1` the implementations can be found in `audiohw.xc`. 

Firstly, code is required to initialise the external audio hardware. In the case of the CODEC on
the L1 Refence Design board there is no required action so the funciton is left empty:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/audiohw.xc
  :start-after: //:audiohw_init
  :end-before: //:

On every sample-rate change a call is made to `AudioHwConfig()`. In the case of the CODEC on the 
L1 Reference Design baord the CODEC must be reset and set the relevant clock input from the two 
oscillators on the board. 

Both the CODEC reset line and clock selection line are attached to the 32 bit port 32A. This is 
accessed through the ``port32A_peek`` and ``port32A_out`` functions:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/audiohw.xc
  :start-after: // Port 32A helpers 
  :end-before: //:audiohw_init

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/audiohw.xc
  :start-after: //:audiohw_config
  :end-before: //:

Finally, the application has functions for audio streaming start/stop
that enable/disable an LED on the board (also on port 32A):

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/audiostream.xc

The main program
~~~~~~~~~~~~~~~~

The ``main()`` function is shared across all applications is therefore part of the framework.  
It is located in ``sc_usb_audio`` and contains:

* A declaration of all the ports used in the framework. These vary
  depending on the PCB an application is running on.
* A ``main`` function which declares some channels and then has a
  ``par`` statement which runs the required cores in parallel.

The framework supports devices with multiple tiles so it uses the ``on tile[n]:`` syntax.

The first core run is the XUD library:

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* USB Interface
   :end-before: /* USB Packet buff

The make up of the channel arrays connecting to this driver are
described in :ref:`usb_audio_sec_component_api`.

The channels connected to the XUD driver are fed into the buffer
and decouple cores:

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: //:buffer
   :end-before: //:

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* Decoupling core */
   :end-before: //:


These then connect to the audio driver which controls the I2S output and
S/PDIF output (if enabled). If S/PDIF output is enabled, this
component spawns into two cores as opposed to one.

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* Audio I/O Core (pars
   :end-before: //:

Finally, if MIDI is enabled you need a core to drive the MIDI input
and output.  The MIDI core also optionally handles authentication with Apple devices. 
Due to licensing issues this code is only available to Apple MFI licensees.  Please contact XMOS 
for details.

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* MIDI core */
   :end-before: #endif

