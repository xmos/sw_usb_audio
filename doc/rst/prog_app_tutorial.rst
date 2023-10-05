A Typical USB Audio Application
--------------------------------

This section provides a walk through of a typical USB Audio application. Where specific examples are required
code is used from the application for `XK-AUDIO-316-MC` (``app_usb_aud_xk_316_mc``).

.. note::

    The applications in ``sw_usb_audio`` use the "Codeless Programming Model" as documented in ``lib_xua``.
    Briefly, the ``main()`` function is used from ``lib_xua`` with build-time defines in the application configuring
    the framework provided by ``lib_xua``. Various functions from ``lib_xua`` are then overridden to provide
    customisation. See ``lib_xua`` for full details.

Each application directory contains:

    #. A ``Makefile``

    #. A ``src`` directory

The ``src`` directory is arranged into two directories:

    #. A ``core`` directory containing source items that must be made available to the USB Audio framework

    #. An ``extensions`` directory that includes extensions to the framework such as external device configuration etc

The ``core`` folder for each application contains:

    #. A ``.xn`` file to describe the hardware platform the application will run on
    #. An (optional) configuration header file to customised the framework provided by ``lib_xua`` named ``xua_conf.h``

.. note::

    The `XCOMMON` build sytem autmatically locates ``_conf.h`` files in the source tree for all used ``lib`` dependencies.


Lib_xua Configuration
~~~~~~~~~~~~~~~~~~~~~

The ``xua_conf.h`` file contains all the build-time ``#defines`` required to tailor framework provided by ``lib_xua``
to the particular application at hand.  Typically these over-ride default values in ``xua_conf_default.h``
in ``lib_xua/api``.

Firstly in ``app_usb_aud_xk_316_mc`` the ``xua_conf.h`` file sets defines to determine overall capability. For this application
most of the optional interfaces are disabled by default. This is because the applications provide a large number build configurations
in the ``Makefile`` enabling various interfaces. For a product with a fixed specification this almost certainly would not be the case and setting
in this file may be the preferred option.

Note that ``ifndef`` is used to check that the option is not already defined in the ``Makefile``.

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to basic functionality
  :end-before: Defines relating to channel count

Next, the file defines properties of the audio channels including counts and arrangements. By default the
application provides 8 analogue channels for input and output.

The total number of channels exposed to the USB host (set via ``NUM_USB_CHAN_OUT`` and ``NUM_USB_CHAN_IN``) are calculated
based on the audio interfaces enabled. Again, this is due to the multiple build configurations in the application ``Makefile``
and likely to be hard-coded for a product.

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to channel
  :end-before: Channel index of S/PDIF

Channel indices/offsets are set based on the audio interfaces enabled. Channels are indexed from 0. Setting ``SPDIF_TX_INDEX`` to 0
would cause the S/PDIF channels to duplicate analogue channels 0 and 1. Note, the offset for analogue channels is always 0.

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to channel arrangement
  :end-before: Defines relating to audio frequencies

The file then sets some frequency related defines for the audio master clocks and the maximum sample-rate for the device.

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to audio frequencies
  :end-before: Defines relating to feature

Due to the multi-tile nature of the `xCORE` architecture the framework needs to be informed as to which tile various interfaces
should be placed on, for example USB, S/PDIF etc.

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to feature placement
  :end-before: Defines relating to USB descriptor

The file also sets some defines for general USB ID's and strings. These are set for the XMOS reference design but vary per
manufacturer:

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/core/xua_conf.h
  :start-after: Defines relating to USB descriptor
  :end-before: Board power source

For a full description of all the defines that can be set in ``xua_conf.h`` see :ref:`sec_xua_conf_api`

User Functions
~~~~~~~~~~~~~~

In addition to the ``xua_conf.h`` file, the application needs to provide implementations of some overridable user
functions in ``lib_xua`` to provide custom functionality.

For ``app_usb_aud_xk_316_mc`` the implementations can be found in ``src/extensions/audiohw.xc`` and ``src/extensions/audiostream.xc``

The file ``audiohw.xc`` provides override implementations of the following function that is run on device start-up:

- ``AudioHwInit()``

The file ``audiohw.xc`` also provides override implementations of the following functions that are run on sample-rate change:

- ``AudioHwConfig()``
- ``AudioHwConfig_Mute()``
- ``AudioHwConfig_UnMute()``

Note, the default implementations of all these functions in ``lib_xua`` are empty. These functions have parameters for sample
frequency, sample depth, etc as appropriate.

In the case of ``app_usb_aud_xk_316_mc`` these functions configure the external DAC's and ADC's via an I2C bus. ``lib_xua``
automatically configures the application PLL to generate the correct master clock frequency.

The calling order is a follows:

- ``AudioHwConfig_Mute()``
- The application PLL is configured to the new master clock frequency ``lib_xua``
- ``AudioHwConfig()``
- ``AudioHwConfig_UnMute()``

The implementations of ``AudioHwConfig_Mute()`` and ``AudioHwConfig_UnMute()`` ensure that there are no audible clicks/pops during
the sample change process implemented in ``AudioHwConfig()``. Due to the complexity of the hardware on the `XK-AUDIO-316-MC` the
source code is not included here.

The application also overrides ``UserAudioStreamStart()`` and ``UserAudioStreamStop()``. These are called from ``lib_xua`` when the audio
stream to the device is started or stopped respectively. The applications uses these functions to enable/disable the LEDs on the board
based on whether an audio stream is present (input or output).

.. literalinclude:: sw_usb_audio/app_usb_aud_xk_316_mc/src/extensions/audiostream.xc

.. note::

    A media player application may choose to keep an audio stream open and simply send zero data when playback is paused.

The Main Program
~~~~~~~~~~~~~~~~

The ``main()`` function is the entry point to an application. In the `XMOS USB Audio Reference Design` software it is shared by all
applications and is therefore part of the framework.

This section is largely informational as most developers should not need to modify the ``main()`` function.
``main()`` is located in ``main.xc`` in  ``lib_xua``, this file contains:

  * A declaration of all the ports used in the framework. These clearly vary depending on the hardware platform the
    application is running on.
  * A ``main()`` function which declares some channels and then has a ``par`` statement which runs the required cores in parallel.

Full documentation can be found in ``lib_xua``.

The first core run is a ``usb_audio_core`` task. This runs cores for the USB interface and buffering tasks for audio
and endpoint buffering:

.. literalinclude:: lib_xua/lib_xua/src/core/main.xc
   :start-after: /* Core USB audio task
   :end-before: XUA_USB_EN

This task runs various cores including one for the USB interfacing core (``XUD_Main()``):

.. literalinclude:: lib_xua/lib_xua/src/core/main.xc
   :start-after: /* USB interface core
   :end-before: XUD_PWR_CFG

The specification of the channel arrays connecting to this driver are described in :ref:`usb_audio_sec_component_api`.

The channels connected to ``XUD_Main()`` are passed to the ``XUA_Buffer()`` function which implements audio buffering and also
buffering for other Endpoints.

.. literalinclude:: lib_xua/lib_xua/src/core/main.xc
   :start-after: /* Endpoint & audio buffering
   :end-before: //:

A channel connects this buffering task to the audio driver which controls the I2S output. It also forwards and receives
audio samples from other interfaces e.g. S/PDIF, ADAT, as required:

.. literalinclude:: lib_xua/lib_xua/src/core/main.xc
   :start-after: /* Audio I/O task
   :end-before: //:

Finally, other task are create for various interfaces, for example, if MIDI is enabled a core is required to drive the MIDI input
and output.

.. literalinclude:: lib_xua/lib_xua/src/core/main.xc
   :start-after: /* MIDI core */
   :end-before: #endif

