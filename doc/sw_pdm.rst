PDM Microphones
---------------

Overview of PDM implemention
----------------------------

The design is capable of integrating PDM microphones. The PDM stream from the microphones is converted
to PCM and output to the host via USB. 

Interfacing to the PDM microphones is done using the XMOS microphone array library (``lib_mic_array``).
``lib_mic_array`` is designed to allow interfacing to PDM microphones coupled with efficient decimation
to user selectable output sample rates. 

.. note:: 
    The ``lib_mic_array`` library is only available for xCORE-200 series devices.

The following components of the library are used:

 * PDM interface
 * Four channel decimators

|newpage|


Up to sixteen PDM microphones can be attached to each high channel count PDM interface (``mic_array_pdm_rx()``). 
One to four processing tasks, ``mic_array_decimate_to_pcm_4ch()``, each process up to four channels. For 1-4 
channels the library requires two logical cores:

 .. figure:: images/pdm_chan4.pdf
            :width: 100%

            One to four channel count PDM interface


for 5-8 channels three logical cores are required, as shown below:

 .. figure:: images/pdm_chan8.pdf
            :width: 100%

            Five to eight count PDM interface

The left most task, ``mic_array_pdm_rx()``, samples up to 8 microphones and filters the data to provide up to
eight 384 KHz data streams, split in two streams of four channels. The processing thread
decimates the signal to a user chosen sample rate (one of 48, 24, 16, 12 or 8 KHz).

More channels can be supported by increasing the number of cores dedicated to the PDM tasks. However, the current
PDM mic integration into USB Audio limits itself to 8.

After the decimation to the output sample-rate various other steps take place e.g. DC offset elimination, gain correction
and compensation etc. Please refer to ``lib_mic_array`` documention for further implementation detail and complete feature set. 


PDM Microphone Hardware Characteristics
+++++++++++++++++++++++++++++++++++++++

The PDM microphones need a *clock input* and provide the PDM signal on a *data output*. All PDM microphones share the same 
clock signal (buffered on the PCB as appropriate), and output onto eight data wires that are connected to a single 8-bit port:

.. _pdm_wire_table:

.. list-table:: PDM microphone data and signal wires
     :class: vertical-borders horizontal-borders
     
     * - *CLOCK*
       - Clock line, the PDM clock the used by the microphones to 
         drive the data out.
     * - *DQ_PDM*
       - The data from the PDM microphones on an 8 bit port.
       
The only port that is passed into ``lib_mic_array`` is the 8-bit data port. The library
assumes that the input port is clocked using the PDM clock and requires no knowlege of the 
PDM clock source. 

The input clock for the microphones can be generated in a multitude of
ways. For example, a 3.072MHz clock can be generated on the board, or the xCORE can
divide down 12.288 MHz master clock. Or, if clock accuracy is not important, the internal 100 MHz 
reference can be divided down to provide an approximate clock.

Integration of PDM Microphones into USB Audio
+++++++++++++++++++++++++++++++++++++++++++++

A PDM microphone wrapper is called from ``main()`` and takes one channel argument connecting it to the rest of the system:

    ``pcm_pdm_mic(c_pdm_pcm);``

The implemetation of this function can be found in the file ``pcm_pdm_mics.xc``.

The first job of this function is to configure the ports/clocking for the microphones, this divides the external 
audio master clock input (on port ``p_mclk``) and outputs the divided clock to the microphones via the ``p_pdm_clk`` port:: 

    configure_clock_src_divide(pdmclk, p_mclk, MCLK_TO_PDM_CLK_DIV);
    configure_port_clock_output(p_pdm_clk, pdmclk);
    configure_in_port(p_pdm_mics, pdmclk);
    start_clock(pdmclk);

It then runs the various cores required for the PDM interface and PDM to PCM conversion as discussed previously::

    par
    {
        mic_array_pdm_rx(p_pdm_mics, c_4x_pdm_mic_0, c_4x_pdm_mic_1);
        mic_array_decimate_to_pcm_4ch(c_4x_pdm_mic_0, c_ds_output[0]);
        mic_array_decimate_to_pcm_4ch(c_4x_pdm_mic_1, c_ds_output[1]);
        pdm_process(c_ds_output, c_pcm_out);
    }

The ``pdm_process()`` task includes the main integration code, it takes audio from the ``lib_mic_array`` cores, buffers 
it, performs optional local processing and outputs it to the audio driver (TDM/I2S core).

This function simply makes a call to ``mic_array_get_next_time_domain_frame()`` in order to get a frame of PCM audio 
from the microphones.  It then waits for an request for audio samples from the audio/I2S/TDM core via a channel and
sends the frame of audio back over this channel.

Note, it is assumed that the system shares a global master-clock, therefore no additional buffering or rate-matching/conversion
is required.
