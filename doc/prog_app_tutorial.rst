A USB Audio Application (walkthrough)
-------------------------------------
.. highlight:: none

This tutorial provides a walk through of the single tile USB Audio Reference Design (L-Series) example, which can be found in the ``app_usb_aud_l1`` directory. 

In each application directory the ``src`` directory is arranged into two folders:

#. An ``core`` directory containing source items that must be made available to the USB Audio framework
#. An ``extensions`` directory that includes extensions to the framework such as CODEC config etc

The ``core`` folder for each application contains:

#. A ``.xn`` file to describe the hardware.
#. A custom defines file: ``customdefines.h`` for framework configuration
#. A ``ports.h`` header file to contain the declarations of ports used in addition to those declared in framework



Custom Defines
~~~~~~~~~~~~~~

The ``customdefines.h`` file contains all the #defines required to
tailor the USB audio framework to the particular application at
hand. First there are defines to determine overall capability. For
this reference design input and output, S/PDIF output and DFU are enabled:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: //:Functionality
  :end-before: //:

Next, the file defines the audio properties of the application. This
application has stereo in and stereo out with an S/PDIF output that
duplicates analogue channels 1 and 2:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: //:audio_defs
  :end-before: //:

Finally, there are some general USB identification defines to be
set. These are set for the XMOS reference design but vary per
manufacturer:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/core/customdefines.h
  :start-after: //:usb_defs
  :end-before: //:

For a full description of all the defines that can be set in
``customdefines.h`` see :ref:`usb_audio_sec_custom_defines_api`.

Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~

In addition to the custom defines file, the application needs to
provide definitions of user functions that are specific to the
application. Firstly, code is required to handle the CODEC. On boot up
you do not need to do anything with the CODEC so there is just an empty function:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/codec.xc
  :start-after: //:codec_init
  :end-before: //:

On sample rate changes, you need to reset the CODEC and set the
relevant clock input from the two oscillators on the board. Both the
CODEC reset line and clock selection line are attached to the 32 bit
port 32A. This is toggled through the ``port32A_peek`` and
``port32A_out`` functions:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/codec.xc
  :start-after: //:codec_config
  :end-before: //:

Since the clocks come from fixed oscillators on this board, the
clock configuration functions do not need to do anything. This will
be different if the clocks came from an external PLL chip:

.. literalinclude:: sw_usb_audio/app_usb_aud_l1/src/extensions/clocking.xc

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

The first core run is the XUD driver:

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* USB Interface
   :end-before: /* Endpoint 0

The make up of the channel arrays connecting to this driver are
described in :ref:`usb_audio_sec_component_api`.

The channels connected to the XUD driver are fed into the buffer
and decouple cores:

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* USB Buffer Core
   :end-before: /* Audio I/O (pars

These then connect to the audio driver which controls the I2S output and
S/PDIF output (if enabled). If S/PDIF output is enabled, this
component spawns into two cores as opposed to one.

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: /* Audio I/O (pars
   :end-before: #if defined (MIDI

Finally, if MIDI is enabled you need a core to drive the MIDI input
and output.  The MIDI core also optionally handles authentication with Apple devices. 
Due to licensing issues this code is only available to Apple MFI licensees.  Please contact XMOS 
for details.

.. literalinclude:: sc_usb_audio/module_usb_audio/main.xc
   :start-after: #if defined (MIDI
   :end-before: #ifdef SU1_AD

