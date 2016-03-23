PDM Microphones
---------------

The design is capable of integrating PDM microphones. The PDM stream from the microphones is converted
to PCM and outpu to a host via USB. 

Interfacing to the PDM micrphones is done using the XMOS microphone array library (``lib_mic_array``).
``lib_mic_array`` is designed to allow interfacing to PDM microphones coupled with efficient decimation
to user selectable output sample rates. 

Note, the ``lib_mic_array`` library is only avaliable for xCORE-200 series devices.

The following components of the library are used:

 * PDM interface
 * Four channel decimators


Up to sixteen PDM microphones can be attached to each high channel count PDM interface (``mic_array_pdm_rx()``). 
One to four processing tasks, ``mic_array_decimate_to_pcm_4ch()``, each process up to four channels. For 1-4 
channels the library requires two logical cores:


for 5-8 channels three logical cores are required, as shown below:


More channels can be supported by increasing the 


Please refer to ``lib_mic_array`` documentation for further implementation detail and features.

The PDM microphone integration code is implemented in the file ``pdm_mics.xc``.
