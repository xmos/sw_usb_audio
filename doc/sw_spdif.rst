S/PDIF Transmit
---------------

XMOS devices can support S/PDIF transmit up to 192kHz. The XMOS S/SPDIF transmitter component runs
in a single core and can be found in ``sc_spdif/module_spdif_tx``

The S/PDIF transmitter core takes PCM audio samples via a channel and outputs them
in S/PDIF format to a port.  A lookup table is used to encode the audio data into the required format. 

It receives samples from the Audio I/O core two at a time (for left and right). For each sample,
it performs a lookup on each byte, generating 16 bits of encoded data which it outputs to a port.

S/PDIF sends data in frames, each containing 192 samples of the left and right channels.

Audio samples are encapsulated into S/PDIF words (adding preamble, parity, channel status and validity
bits) and transmitted in biphase-mark encoding (BMC) with respect to an *external* master clock.

Note that a minor change to the ``SpdifTransmitPortConfig`` function would enable *internal* master
clock generation (e.g. when clock source is already locked to desired audio clock).

..  list-table:: S/PDIF Capabilities
   
   * - **Sample frequencies**   
     - 44.1, 48, 88.2, 96, 176.4, 192 kHz
   * - **Master clock ratios** 
     - 128x, 256x, 512x
   * - **Module**  
     - ``module_spdif_tx``

Clocking
++++++++

.. only:: latex

 .. figure:: images/spdif.pdf

   D-Type Jitter Reduction

.. only:: html

 .. figure:: images/spdif.png

   D-Type Jitter Reduction


The S/PDIF signal is output at a rate dictated by the external master clock. The master clock must 
be 1x 2x or 4x the BMC bit rate (that is 128x 256x or 512x audio sample rate, respectively). 
For example, the minimum master clock frequency for 192kHz is therefore 24.576MHz.

This resamples the master clock to its clock domain (oscillator), which introduces jitter of 2.5-5 ns on the S/PDIF signal. 
A typical jitter-reduction scheme is an external D-type flip-flop clocked from the master clock (as shown in the preceding diagram).

Usage
+++++

The interface to the S/PDIF transmitter core is via a normal channel with streaming built-ins
(``outuint``, ``inuint``). Data format should be 24-bit left-aligned in a 32-bit word: ``0x12345600``

The following protocol is used on the channel:

.. list-table:: S/PDIF Component Protocol

  * - ``outuint`` 
    - Sample frequency (Hz)
  * - ``outuint`` 
    - Master clock frequency (Hz)
  * - ``outuint``
    - Left sample
  * - ``outuint``
    - Right sample 
  * - ``outuint`` 
    - Left sample
  * - ``outuint`` 
    - Right sample
  * - ``...``
    -
  * - ``...``
    -
  * - ``outct`` 
    -  Terminate



Output stream structure
+++++++++++++++++++++++

The stream is composed of words with the following structure shown in
:ref:`usb_audio_spdif_stream_structure`. The channel status bits are
0x0nc07A4, where c=1 for left channel, c=2 for right channel and n
indicates sampling frequency as shown in :ref:`usb_audio_spdif_sample_bits`.

.. _usb_audio_spdif_stream_structure:

.. list-table:: S/PDIF Stream Structure
     :header-rows: 1
     :widths: 10 32 58
     
     * - Bits 
       - 
       -
     * - 0:3
       - Preamble 
       - Correct B M W order, starting at sample 0
     * - 4:27 
       - Audio sample 
       - Top 24 bits of given word
     * - 28 
       - Validity bit 
       - Always 0
     * - 29 
       - Subcode data (user bits) 
       - Unused, set to 0
     * - 30 
       - Channel status 
       - See below
     * - 31 
       - Parity 
       - Correct parity across bits 4:30
     

.. _usb_audio_spdif_sample_bits:

.. list-table:: Channel Status Bits
  :header-rows: 1

  * - Frequency (kHz)
    - n
  * - 44.1
    - 0
  * - 48
    - 2
  * - 88.2
    - 8
  * - 96
    - A
  * - 176.4
    - C
  * - 192
    - E









