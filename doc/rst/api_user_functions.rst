User function definitions
=========================

The following functions can be optionally defined by an application to override default (empty)
implementation in ``lib_xua``.

External audio hardware configuration
-------------------------------------

The functions should be implemented to configure external audio hardware.

.. doxygenfunction:: AudioHwInit
.. doxygenfunction:: AudioHwConfig
.. doxygenfunction:: AudioHwConfig_Mute
.. doxygenfunction:: AudioHwConfig_UnMute


Audio streaming notification
----------------------------

They functions can be useful for mute lines, indication LEDs etc.

.. doxygenfunction:: UserAudioStreamStart
.. doxygenfunction:: UserAudioStreamStop
.. doxygenfunction:: UserAudioInputStreamStart
.. doxygenfunction:: UserAudioInputStreamStop
.. doxygenfunction:: UserAudioOutputStreamStart
.. doxygenfunction:: UserAudioOutputStreamStop


HID controls
------------

The following function is called when the device wishes to read physical user input (buttons etc).
The function should write relevant HID bits into this array.
The bit ordering and functionality is defined by the HID report descriptor used.

.. doxygenfunction:: UserHIDGetData
