Required User Function Definitions
==================================

The following functions need to be defined by an application using the XMOS USB Audio framework.

External Audio Hardware Configuration Functions
-----------------------------------------------

.. doxygenfunction:: AudioHwInit
.. doxygenfunction:: AudioHwConfig
.. doxygenfunction:: AudioHwConfig_Mute
.. doxygenfunction:: AudioHwConfig_UnMute


Audio Streaming Functions
-------------------------

The following functions can be optionally used by the design by overriding their empty by default implementation in ``lib_xua``.
They can be useful for mute lines etc.

.. doxygenfunction:: UserAudioStreamStart
.. doxygenfunction:: UserAudioStreamStop
.. doxygenfunction:: UserAudioInputStreamStart
.. doxygenfunction:: UserAudioInputStreamStop
.. doxygenfunction:: UserAudioOutputStreamStart
.. doxygenfunction:: UserAudioOutputStreamStop


HID Controls
------------

The following function is called when the device wishes to read physical user input (buttons etc).
The function should write relevant HID bits into this array. The bit ordering and functionality is defined by the HID report descriptor used.

.. doxygenfunction:: UserHIDGetData
