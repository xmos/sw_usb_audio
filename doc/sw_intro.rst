|newpage|

.. _usb_audio_sec_architecture:

The USB Audio System Architecture
---------------------------------

The XMOS USB Audio platform consists of a series of communicating
components. Every system is required to have the shared components listed in
:ref:`usb_audio_shared_components`.

.. _usb_audio_shared_components:

.. list-table:: Shared Components
 :header-rows: 1
 :widths: 40 60

 * - Component
   - Description
 * - XMOS USB Device Driver (XUD)
   - Handles the low level USB I/O.
 * - Endpoint 0
   - Provides the logic for Endpoint 0 which handles
     enumeration and control of the device including DFU related requests.
 * - Endpoint buffer
   - Buffers endpoint data packets to and from the host.
 * - Decoupler
   - Manages delivery of audio packets between the endpoint buffer
     component and the audio components. It can also handle volume control processing.
 * - Audio Driver
   - Handles audio I/O over I2S and manages audio data
     to/from other digital audio I/O components.
     
In addition :ref:`usb_audio_optional_components` shows
components that can be added to a design:

.. _usb_audio_optional_components:

.. list-table:: Optional Components
 :header-rows: 1
 :widths: 40 60

 * - Component
   - Description
 * - Mixer
   - Allows digital mixing of input and output channels.  It can also 
     handle volume control instead of the decoupler.
 * - S/PDIF Transmitter
   - Outputs samples of an S/PDIF digital audio interface.
 * - S/PDIF Receiver
   - Inputs samples of an S/PDIF digital audio interface (requires the
     clockgen component).
 * - ADAT Receiver
   - Inputs samples of an ADAT digital audio interface (requires the
     clockgen component).
 * - Clockgen
   - Drives an external frequency generator (PLL) and manages
     changes between internal clocks and external clocks arising
     from digital input.
 * - MIDI
   - Outputs and inputs MIDI over a serial UART interface.

.. _usb_audio_threads:

.. figure:: images/threads-crop.*
      :width: 100%
 
      USB Audio Core Diagram

:ref:`usb_audio_threads` shows how the components interact with each
other.  The green circles represent cores with arrows indicating inter-core communications.

This section will now examine these components in detail.
