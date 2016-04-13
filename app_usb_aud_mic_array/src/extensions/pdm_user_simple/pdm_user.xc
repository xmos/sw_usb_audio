
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include "mic_array.h"
#include "pcm_pdm_mic.h"


/* Most basic processing example */
#ifndef MIC_PROCESSING_USE_INTERACE
void user_pdm_init()
{
    /* do nothing */
}
#endif

#ifdef MIC_PROCESSING_USE_INTERFACE
[[distributable]]
unsafe void user_pdm_process(server mic_process_if i_mic_data)
#else
unsafe void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
#endif
{
#ifdef MIC_PROCESSING_USE_INTERFACE
    while(1)
    {
        select
        {
            case i_mic_data.init():
                /* Do nothing */
                break;

            case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio, int output[]):
#endif
            for(unsigned i=0; i<7; i++)
            {
                /* Simply copy input buffer to output buffer unmodified */
                output[i] += audio->data[i][0];
            }
#ifdef MIC_PROCESSING_USE_INTERFACE
            break;
        } // select{}
    }  // while(1)
#endif
}

