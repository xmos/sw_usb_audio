
XMOS USB Device (XUD) Library
-----------------------------

All low level communication with the USB host is handled by the XMOS USB Device (XUD) library.

The ``XUD_Manager()`` function runs in its own core and communicates with endpoint cores though a 
mixture of shared memory and channel communications.

For more details and full XUD API documentation please refer to `XMOS USB Device (XUD) Library
<http://www.xmos.com/published/xuddg>`_

:ref:`usb_audio_threads` shows the XUD library communicating with two other cores:

-  Endpoint 0: This core controls the enumeration/configuration tasks of the USB device.

-  Endpoint Buffer: This core sends/receives data packets from the XUD library.  
   The core receives audio data from the decoupler core, MIDI data from the MIDI core etc.

