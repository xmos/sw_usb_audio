ADAT Receive
------------

The ADAT receive component receives up to eight channels of audio at a sample rate
of 44.1kHz or 48kHz. The API for calling the receiver functions is
described in :ref:`usb_audio_sec_component_api`.

The component outputs 32 bits words split into nine word frames. The
frames are laid out in the following manner:

  * Control byte
  * Channel 0 sample
  * Channel 1 sample
  * Channel 2 sample
  * Channel 3 sample
  * Channel 4 sample
  * Channel 5 sample
  * Channel 6 sample
  * Channel 7 sample

Example of code show how to read the output of the ADAT component is shown below::

  control = inuint(oChan);

  for(int i = 0; i < 8; i++) 
  {
      sample[i] = inuint(oChan);
  }

Samples are 24-bit values contained in the lower 24 bits of the word. 

The control word comprises four control bits in bits [11..8] and the value 0b00000001 in bits [7..0].
This control word enables synchronization at a higher level, in that on the channel a single odd 
word is always read followed by eight words of data.

.. Timing Requirements
   ~~~~~~~~~~~~~~~~~~~

.. The data samples are outputted onto the channel every 2.4 us. The
.. control sample follows 1.7 us after the last data sample, and is
.. followed 2.4 us later by the first data sample. Given that a channel
.. can hold two words of data, when data appears on the channel, it
.. should be input within 4.1 us otherwise the ADAT receiver will block,
.. and data will be lost. Between data samples a window of 4.8 us is
.. available.

Integration
~~~~~~~~~~~

Since the ADAT is a digital stream the devices master clock must synchronised to it.  This is
typically achieved with an external fractional-n clock multiplier.

The ADAT receive function communicates with the clockGen component which passes audio data onto the
audio driver and handles locking to the ADAT clock source if required.
