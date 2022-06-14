Required User Function Definitions
----------------------------------

The following functions need to be defined by an application using the XMOS USB Audio framework.

External Audio Hardware Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. c:function:: void AudioHwInit(chanend ?c_codec)

   This function is called when the audio core starts after the
   device boots up and should initialize the external audio harware e.g. clocking, DAC, ADC etc

   :param c_codec: An optional chanend that was original passed into
                   :c:func:`audio` that can be used to communicate 
                   with other cores.
  

.. c:function:: void AudioHwConfig(unsigned samFreq, unsigned mclk, chanend ?c_codec, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)

   This function is called when the audio core starts or changes
   sample rate. It should configure the extenal audio hardware to run at the specified
   sample rate given the supplied master clock frequency.

   :param samFreq: The sample frequency in Hz that the hardware should be configured to (in Hz).
                   
   :param mclk: The master clock frequency that is required in Hz.
   
   :param c_codec: An optional chanend that was original passed into
                   :c:func:`audio` that can be used to communicate 
                   with other cores.

   :param dsdMode: Signifies if the audio hardware should be configured for DSD operation

   :param sampRes_DAC: The sample resolution of the DAC stream
   
   :param sampRes_ADC: The sample resolution of the ADC stream
  

Audio Streaming Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

The following functions can be optionally used by the design. They can be useful for mute lines etc.

.. c:function:: void AudioStreamStart(void)

  This function is called when the audio stream from device to host
  starts. 

.. c:function:: void AudioStreamStop(void)

  This function is called when the audio stream from device to host stops.

Host Active
~~~~~~~~~~~

The following function can be used to signal that the device is connected to a valid host.

This is called on a change in state.

.. c:function:: void AudioStreamStart(int active)

   :param active: Indicates if the host is active or not. 1 for active else 0.


HID Controls
~~~~~~~~~~~~

The following function is called when the device wishes to read physical user input (buttons etc).

.. c:function:: void UserReadHIDButtons(unsigned char hidData[])

    :param hidData: The function should write relevant HID bits into this array. The bit ordering and functionality is defined by the HID report descriptor used.
