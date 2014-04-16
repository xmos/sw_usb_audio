|newpage|

.. _usb_audio_sec_usb:

Endpoint 0: Management and Control
----------------------------------

All USB devices must support a manadatory control endpoint, Endpoint 0.  This controls the management tasks of the USB device.

These tasks can be generally split into enumeration, reset, audio configuration and firmware upgrade.

Startup/Enumeration
~~~~~~~~~~~~~~~~~~~

When the device is first attached to a host, enumeration occurs.  This process involves the host interogating the device as to its functionality. The device does this by presenting several interfaces to the host via a set of descriptors.

During the enumeration process the host will issue various commands to the device including assigning the device a unique address on the bus.

The endpoint 0 code runs in its own core and follows a similar format to that of the USB Device examples in sc_usb_device. That is, a call is made to ``USB_DetSetupPAcket()`` to receive a command from the host.  Any device specific requests are handled - in this case audio class, MIDI class, DFU requests etc.  

The endpoint 0 code then makes a call to ``USB_StandardRequests()`` (provided in ``module_usb_device``). This performs the manadtory requests that a USB Device must support in order to reduce the amount of coding required. For more information and full documentation please see the `XMOS USB Device Design Guide <https://www.xmos.com/zh/node/17007?page=9>`_


Common enumeration requests are largely handled by the call to ``DescriptorRequests()`` using data
structures found in the ``descriptors_2.h`` file. These
structures use defines which can be customized---see :ref:`usb_audio_sec_custom_defines_api`.

This function returns 0 if the request was fully handled (and thus no further action is required).  
The function returns 1 if the request was not recognised by the ``DescriptorRequests()`` function and further parsing 
is required to deal with the request.
The function returns -1 if a USB bus reset has been communicated from XUD to Endpoint 0.

.. _fig_usb_devices:

.. table:: USB interfaces presented to host
  :class: center

  +-----------------------+----------------------------------+
  | **Mode**              | **Interfaces**                   |
  +=======================+==================================+ 
  | Application mode      | | Audio Class 2/Audio Class 1    |
  |                       | | DFU Class 1.1                  |
  |                       | | MIDI Device Class 1.0          |
  +-----------------------+----------------------------------+
  | DFU mode              | DFU Class 1.1                    |
  +-----------------------+----------------------------------+

The device initially starts in Application mode.




:ref:`usb_audio_sec_dfu` describes how DFU mode is used. The
audio device class (1 or 2) is set at compile time---see :ref:`usb_audio_sec_custom_defines_api`.



Reset
~~~~~

On receiving a reset request, three steps occur:

#. Depending on the DFU state, the device may be set into DFU
   mode.

#. A XUD function is called to reset the endpoint structure and receive the new bus speed.

.. _usb_audio_sec_audio-requ-sett: 

Audio Request: Setting The Sample Rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the host requests a change of sample
rate, it sends a command to Endpoint 0. 

Since the ``DescriptorRequests()`` function does not deal with audio requests it returns 1.  After some parsing the
request is handled by either the ``AudioRequests_1()`` or ``AudioRequests_2()`` function (based on whether the device is running 
in Audio Class 1.0 or 2.0 mode).

.. _usb_audio_sec_audio-requ-volume: 

Audio Request: Volume Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the host requests a volume change, it
sends an audio interface request to Endpoint 0. An array is
maintained in the Endpoint 0 core that is updated with such a
request.

When changing the volume, Endpoint 0 applies the master volume and
channel volume, producing a single volume value for each channel.
These are stored in the array.

The volume will either be handled by the decoupler or the mixer
component (if the mixer component is used). Handling the volume in the
mixer gives the decoupler more performance to handle more channels.

If the effect of the volume control array on the audio input and
output is implemented by the decoupler, the decoupler core 
reads the volume values from this array. Note that this array is shared
between Endpoint 0 and the decoupler core. This is done in a safe
manner, since only Endpoint 0 can write to the array, word update
is atomic between cores and the decoupler core only reads from
the array (ordering between writes and reads is unimportant in this
case). Inline assembly is used by the decoupler core to access
the array, avoiding the parallel usage checks in XC.

If volume control is implemented in the mixer, Endpoint 0 sends a mixer command to the mixer to change the volume. Mixer commands
are described in :ref:`usb_audio_sec_mixer`.

Audio Endpoints (Endpoint Buffer and Decoupler)
-----------------------------------------------

Endpoint Buffer
~~~~~~~~~~~~~~~

All endpoints other that Endpoint 0 are handled in one core. This
core is implemented in the file ``usb_buffer.xc``. This loop is responsive to the XUD library. 

This core is also responsible for feedback calculation based on
SOF notification and reads from the port counter of a port
connected to the master clock.

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

Both audio and MIDI use a similar buffering scheme for USB data.
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


Decoupler/Audio core interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
 | inuint()        |                 | Sample transfer (Device to Host)        |
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | inuint()        |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | ...             |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       |                 | Sample transfer (Host to Device)        |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | outuint()       |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+
 | ...             |                 |                                         |
 +-----------------+-----------------+-----------------------------------------+



Aysnc Feedback
++++++++++++++

The device uses a feedback endpoint to report the rate at which
audio is output/input to/from external audio interfaces/devices. This feedback is in accordance with
the *USB Audio Class 2.0 specification*.

After each received USB SOF token, the buffering core takes a
timestamp from a port clocked off the master clock. By subtracting
the timestamp taken at the previous SOF, the number of master clock
ticks since the last SOF is calculated. From this the number of
samples (as a fixed point number) between SOFs can be calculated.
This count is aggregated over 128 SOFs and used as a basis for the
feedback value.

The sending of feedback to the host is also handled in the USB
buffering core.

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
