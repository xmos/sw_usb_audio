|newpage|

.. _usb_audio_sec_usb:

Endpoint 0: Management and Control
----------------------------------

All USB devices must support a mandatory control endpoint, Endpoint 0.  This controls the management tasks of the USB device.

These tasks can be generally split into enumeration, audio configuration and firmware upgrade requests.

Enumeration
~~~~~~~~~~~

When the device is first attached to a host, enumeration occurs.  This process involves the host interrogating the device as to its functionality. The device does this by presenting several interfaces to the host via a set of descriptors.

During the enumeration process the host will issue various commands to the device including assigning the device a unique address on the bus.

The endpoint 0 code runs in its own core and follows a similar format to that of the USB Device examples in sc_usb_device (i.e. Example HID Mouse Demo). That is, a call is made to ``USB_GetSetupPacket()`` to receive a command from the host. This populates a ``USB_SetupPacket_t`` structure, which is then parsed. 

There are many mandatory requests that a USB Device must support as required by the USB Specification. Since these are required for all devices in order to function a 
``USB_StandardRequests()`` function is provided (see ``module_usb_device``) which implements all of these requests. This includes the following items:

    - Requests for standard descriptors (Device descriptor, configuration descriptor etc) and string descriptors
    - USB GET/SET INTERFACE requests
    - USB GET/SET_CONFIGURATION requests
    - USB SET_ADDRESS requests

For more information and full documentation, including full worked examples of simple devices, please refer the `XMOS USB Device Design Guide <https://www.xmos.com/zh/node/17007?page=9>`_

The ``USB_StandardRequests()`` function takes the devices various descriptors as parameters, these are passed from data structures found in the ``descriptors.h`` file. 
These data structures are fully customised based on the how the design is configured using various defines (see :ref:`sec_custom_defines_api`).

The ``USB_StandardRequests()`` functions returns a ``XUD_Result_t``. ``XUD_RESULT_OKAY`` indicates that the request was fully handled without error and no further action is required
- The device should move to receiving the next request from the host (via ``USB_GetSetupPacket()``).

The function returns ``XUD_RES_ERR`` if the request was not recognised by the ``USB_StandardRequests()`` function and a STALL has been issued. 

The function may also return ``XUD_RES_RST`` if a bus-reset has been issued onto the bus by the host and communicated from XUD to Endpoint 0.

Since the ``USB_StandardRequests()`` function STALLs an unknown request, the endpoint 0 code must parse the ``USB_SetupPacket_t`` structure to handle device specific requests and then calling ``USB_StandardRequests()`` as required.  This is described next.

Over-riding Standard Requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The USB Audio design "over-rides" some of the requests handled by ``USB_StandardRequests()``, for example it uses the SET_INTERFACE request to indicate it if the host is streaming audio to the device.  In this case the setup packet is parsed, the relevant action taken, the ``USB_StandardRequests()`` is called to handle the response to the host etc.

Class Requests
~~~~~~~~~~~~~~
Before making the call to ``USB_StandardRequests()`` the setup packet is parsed for Class requests. These are handled in functions such as ``AudioClasRequests_2()``, ``AudioClassRequests_2``, ``DFUDeviceRequests()`` etc depending on the type of request.

Any device specific requests are handled - in this case Audio Class, MIDI class, DFU requests etc.  

Some of the common Audio Class requests and their associated behaviour will now be examined. 

Audio Requests
++++++++++++++

When the host issues an audio request (e.g. sample rate or volume change), it sends a command to Endpoint 0. Like all requests this is returned from ``USB_GetSetupPacket()``. After some parsing (namely as Class Request to an Audio Interface) the request is handled by either the ``AudioClassRequests_1()`` or ``AudioClassRequests_2()`` function (based on whether the device is running in Audio Class 1.0 or 2.0 mode).

Note, Audio Class 1.0 Sample rate changes are send to the relevant endpoint, rather than the interface - this is handled as a special case in he endpoint 0 request parsing where ``AudioEndpointRequests_1()`` is called.

The ``AudioClassRequests_X()`` functions parses the request further in order to ascertain the correct audio operation to execute.

Audio Request: Set Sample Rate
++++++++++++++++++++++++++++++

The ``AudioClassRequests_2()`` function parses the passed ``USB_SetupPacket_t`` structure for a ``CUR`` request of type ``SAM_FREQ_CNTROL`` to a Clock Unit in the devices topology (as described in the devices descriptors).

The new sample frequency is extracted and passed via channel to the rest of the design - through the buffering code and eventually to the Audio IO/I2S core.  The ``AudioClassRequests_2()`` function waits for a handshake to propagate back though the system before signalling to the host that the request has completed successfully. Note, during this time the USB library is NAKing the host essentially holding off further traffic/requests until the sample-rate change is fully complete.

.. _usb_audio_sec_audio-requ-volume: 

Audio Request: Volume Control
+++++++++++++++++++++++++++++

When the host requests a volume change, it
sends an audio interface request to Endpoint 0. An array is
maintained in the Endpoint 0 core that is updated with such a
request.

When changing the volume, Endpoint 0 applies the master volume and
channel volume, producing a single volume value for each channel.
These are stored in the array.

The volume will either be handled by the ``decoupler`` core or the mixer
component (if the mixer component is used). Handling the volume in the
mixer gives the decoupler more performance to handle more channels.

If the effect of the volume control array on the audio input and
output is implemented by the decoupler, the ``decoupler`` core 
reads the volume values from this array. Note that this array is shared
between Endpoint 0 and the decoupler core. This is done in a safe
manner, since only Endpoint 0 can write to the array, word update
is atomic between cores and the decoupler core only reads from
the array (ordering between writes and reads is unimportant in this
case). Inline assembly is used by the decoupler core to access
the array, avoiding the parallel usage checks of XC.

If volume control is implemented in the mixer, Endpoint 0 sends a mixer command to the mixer to change the volume. Mixer commands
are described in :ref:`usb_audio_sec_mixer`.

Audio Endpoints (Endpoint Buffer and Decoupler)
-----------------------------------------------

Endpoint Buffer
~~~~~~~~~~~~~~~

All endpoints other that Endpoint 0 are handled in one core. This
core is implemented in the file ``usb_buffer.xc``. This core is communicates directly with the XUD library. 

The USB buffer core is also responsible for feedback calculation based on USB Start Of Frame
(SOF) notification and reads from the port counter of a port connected to the master clock.

Decoupler
~~~~~~~~~

The decoupler supplies the USB buffering core with buffers to
transmit/receive audio data to/from the host. It marshals these buffers into
FIFOs. The data from the FIFOs are then sent over XC channels to
other parts of the system as they need it. This core also
determines the size of each packet of audio sent to the host (thus
matching the audio rate to the USB packet rate). The decoupler is
implemented in the file ``decouple.xc``.

Audio Buffering Scheme
~~~~~~~~~~~~~~~~~~~~~~~

This scheme is executed by co-operation between the buffering
core, the decouple core and the XUD library.

For data going from the device to the host the following scheme is
used:


#. The decouple core receives samples from the audio core and
   puts them into a FIFO. This FIFO is split into packets when data is
   entered into it. Packets are stored in a format consisting of their
   length in bytes followed by the data.

#. When the buffer cores needs a buffer to send to the XUD core
   (after sending the previous buffer), the decouple core is
   signalled (via a shared memory flag).

#. Upon this signal from the buffering core, the decouple core
   passes the next packet from the FIFO to the buffer core. It also
   signals to the XUD library that the buffer core is able to send a
   packet.

#. When the buffer core has sent this buffer, it signals to the
   decouple that the buffer has been sent and the decouple core
   moves the read pointer of the FIFO.


For data going from the host to the device the following scheme is
used:


#. The decouple core passes a pointer to the buffering core
   pointing into a FIFO of data and signals to the XUD library that
   the buffering core is ready to receive.

#. The buffering core then reads a USB packet into the FIFO and
   signals to the decoupler that the packet has been read.

#. Upon receiving this signal the decoupler core updates the
   write pointer of the FIFO and provides a new pointer to the
   buffering core to fill.

#. Upon request from the audio core, the decoupler core sends
   samples to the audio core by reading samples out of the FIFO.


Decoupler/Audio Core interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To meet timing requirements of the audio system, the decoupler
core must respond to requests from the audio system to
send/receive samples immediately. An interrupt handler
is set up in the decoupler core to do this. The interrupt handler
is implemented in the function ``handle_audio_request``.

The audio system sends a word over a channel to the decouple core to 
request sample transfer (using the build in outuint function).  
The receipt of this word in the channel 
causes the ``handle_audio_request`` interrupt to fire.

The first operation the interrupt handler does is to send back a word 
acknowledging the request (if there was a change of sample frequency
a control token would instead be sent---the audio system uses a testct()
to inspect for this case).

Sample transfer may now take place.  First the audio subsystem transfers
samples destined for the host, then the decouple core sends
samples from the host to device.  These transfers always take place 
in channel count sized chunks (i.e. ``NUM_USB_CHAN_OUT`` and 
``NUM_USB_CHAN_IN``).  That is, if the device has 10 output channels and
8 input channels, 10 samples are sent from the decouple core and 8 received
every interrupt.

The complete communication scheme is shown in the table below (for non sample
frequency change case):


.. table::  Decouple/Audio System Channel Communication

 +-----------------+-----------------+-----------------------------------------+
 | Decouple        | Audio System    | Note                                    |
 +=================+=================+=========================================+
 |                 | outuint()       | Audio system requests sample exchange   |
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        |                 | Interrupt fires and inuint performed    |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       |                 | Decouple sends ack                      |
 +-----------------+-----------------+-----------------------------------------+
 |                 | testct()        | Checks for CT indicating SF change      |
 +-----------------+-----------------+-----------------------------------------+
 |                 | inuint()        | Word indication ACK input (No SF change)|
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        | outuint()       | Sample transfer (Device to Host)        |
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        | outuint()       |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        | outuint()       |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | ...             |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       | inuint()        | Sample transfer (Host to Device)        |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       | inuint()        |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       | inuint()        |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       | inuint()        |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | ...             |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+

.. note::
    The request and acknowledgement sent to/from Decouple to the Audio System is an "output underflow" sample 
    value.  If in PCM mode it will be 0, in DSD mode it will be DSD silence.
    This allows the buffering system to output a suitable underflow value without knowing the format of the stream
    (this is especially advantageous in the DSD over PCM (DoP) case) 

Asynchronous Feedback
+++++++++++++++++++++

The device uses a feedback endpoint to report the rate at which
audio is output/input to/from external audio interfaces/devices. This feedback is in accordance with
the *USB 2.0 Specification*.

This asynchronous clocking scheme means that the device is the clocking master than therefore 
means a high-quality local master clock source can be used.

After each received USB SOF token, the buffering core takes a time-stamp from a port clocked off 
the master clock. By subtracting the time-stamp taken at the previous SOF, the number of master
clock ticks since the last SOF is calculated. From this the number of samples (as a fixed 
point number) between SOFs can be calculated.
This count is aggregated over 128 SOFs and used as a basis for the feedback value.

The sending of feedback to the host is also handled in the USB buffering core via an explicit feedback 
IN endpoint. If both input and output is enabled then the feedback is implicit based on the audio stream 
sent to the host.

USB Rate Control
++++++++++++++++

.. _usb_audio_sec_usb-rate-control: 

The Audio core must consume data from USB
and provide data to USB at the correct rate for the selected sample
frequency. The *USB 2.0 Specification* states that the maximum
variation on USB packets can be +/- 1 sample per USB frame. USB
frames are sent at 8kHz, so on average for 48kHz each packet
contains six samples per channel. The device uses Asynchronous mode,
so the audio clock may drift and run faster or slower than the
host. Hence, if the audio clock is slightly fast, the device may
occasionally input/output seven samples rather than six. Alternatively,
it may be slightly slow and input/output five samples rather than six.
:ref:`usb_audio_samples_per_packet` shows the allowed number of samples
per packet for each example audio frequency.

See USB Device Class Definition for Audio Data Formats v2.0 section 2.3.1.1
for full details.

.. _usb_audio_samples_per_packet:

.. table::  Allowed samples per packet

 +-----------------+-------------+-------------+
 | Frequency (kHz) | Min Packet  | Max Packet  |
 +=================+=============+=============+
 | 44.1            | 5           | 6           |
 +-----------------+-------------+-------------+
 | 48              | 5           | 7           |
 +-----------------+-------------+-------------+
 | 88.2            | 10          | 11          |
 +-----------------+-------------+-------------+
 | 96              | 11          | 13          |
 +-----------------+-------------+-------------+
 | 176.4           | 20          | 21          | 
 +-----------------+-------------+-------------+
 | 192             | 23          | 25          |
 +-----------------+-------------+-------------+


To implement this control, the decoupler core uses the feedback
value calculated in the buffering core. This value is used to
work out the size of the next packet it will insert into the audio
FIFO.



.. .. _fig_usb_devices:

.. .. table:: USB interfaces presented to host
..   :class: center
..
..  +-----------------------+----------------------------------+
..  | **Mode**              | **Interfaces**                   |
.. +=======================+==================================+ 
..  | Application mode      | | Audio Class 2/Audio Class 1    |
..  |                       | | DFU Class 1.1                  |
..  |                       | | MIDI Device Class 1.0          |
..  +-----------------------+----------------------------------+
..  | DFU mode              | DFU Class 1.1                    |
..  +-----------------------+----------------------------------+

.. The device initially starts in Application mode.




.. :ref:`usb_audio_sec_dfu` describes how DFU mode is used. The
.. audio device class (1 or 2) is set at compile time---see :ref:`usb_audio_sec_custom_defines_api`.



.. Reset
.. ~~~~~

.. On receiving a reset request, three steps occur:

.. #. Depending on the DFU state, the device may be set into DFU
   mode.

.. #. A XUD function is called to reset the endpoint structure and receive the new bus speed.

.. _usb_audio_sec_audio-requ-sett: 
