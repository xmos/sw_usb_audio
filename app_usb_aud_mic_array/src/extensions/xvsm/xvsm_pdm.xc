#ifdef XVSM

#include "customdefines.h"
#include <platform.h>
#include <xs1.h>
#include <stdio.h>
#include "mic_array.h"
#include "xua_pdm_mic.h"
#include <print.h>
#include "usr_dsp_cmd.h"
#include "xvsm_support.h"
#include "lib_voice_doa_naive.h"

unsafe
{
    extern unsigned char * unsafe micNum;
    extern unsigned * unsafe doDoa;
    extern vadState_t * unsafe vadState;
}

struct lib_voice_doa doaState;

void user_pdm_init()
{
    lib_voice_doa_naive_init(doaState);
}

#ifdef MIC_PROCESSING_USE_INTERFACE
[[combinable]]
#pragma unsafe arrays
void user_pdm_process(server mic_process_if i_mic_data)
{
    lib_voice_doa_naive_init(doaState);

#else
#pragma unsafe arrays
void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
#endif
#ifdef MIC_PROCESSING_USE_INTERFACE
    user_pdm_init();

    while(1)
    {
        select
        {
            case i_mic_data.init():
                break;

            case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio, int output[]):
#endif
            unsafe
            {
                /* Simply copy input to output buffer unmodified */
                for(int i = 0; i < 8; i++) 
                    output[i] = audio->data[i][0];
                 
                if(*doDoa && (*vadState == VAD_IDLE))
                {   
                    int doaDir = lib_voice_doa_naive_incorporate(doaState, output[1], output[2], output[3], output[4], output[5], output[6]);

                    if(doaDir > 0)
                    {
                        *micNum = 6 - (doaDir / 60);
                    }
                }
                output[1] = audio->data[*micNum][0];
            }

#ifdef MIC_PROCESSING_USE_INTERFACE
            break;
        } // select{}
    }  // while(1)
#endif
}    
#endif
