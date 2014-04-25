Required User Function Definitions
----------------------------------

The following functions need to be defined by an application using the
USB audio framework.

Codec Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. c:function:: void CodecInit(chanend ?c_codec)

   This function is called when the audio core starts after the
   device boots up and should initialize the CODEC.

   :param c_codec: An optional chanend that was original passed into
                   :c:func:`audio` that can be used to communicate 
                   with other cores.
  

.. c:function:: void CodecConfig(unsigned samFreq, unsigned mclk, chanend ?c_codec)

   This function is called when the audio core starts or changes
   sample rate. It should configure the CODEC to run at the specified
   sample rate given the supplied master clock frequency.

   :param samFreq: The sample frequency in Hz that the CODEC should be
                   configured to play.
                   
   :param mclk: The master clock frequency that will be supplied to 
                the CODEC in Hz.
   
   :param c_codec: An optional chanend that was original passed into
                   :c:func:`audio` that can be used to communicate 
                   with other cores.
  

Clocking Configuration Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. c:function:: void ClockingInit(void)

   This function is called when the audio core starts are device
   boot. It should initialize any external clocking hardware.

.. c:function:: void ClockingConfig(unsigned mClkFreq)

   This function is called when the audio core starts or changes
   sample frequency. It should configure any external clocking
   hardware such that the master clock signal being fed into the XCORE Tile
   and CODEC is the same as the specified frequency.

   :param mClkFreq: The required clock frequency in Hz.
   

Audio Streaming Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. c:function:: void AudioStreamStart(void)

  This function is called when the audio stream from device to host
  starts. 

.. c:function:: void AudioStreamStop(void)

  This function is called when the audio stream from device to host stops.


