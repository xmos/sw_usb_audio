
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <xclib.h>
#include <stdint.h>
#include "dsp.h"
#include "print.h"

//TODO
#define NUM_MIC_INPUTS 2
#define BLOCK_SIZE 160

void dsp_process(server dsp_if i_dsp)
{
    int * unsafe in_mic = NULL, * unsafe in_spk = NULL;
    int * unsafe out_mic = NULL, * unsafe out_spk = NULL;
    
    int process_block = 0;

    unsafe {
       
        while(1)
        {
            select
            {

                /* Client wants a processed block. Also gives us input samples */
                case !process_block => i_dsp.transfer_buffers(int * unsafe in_mic_buf, int * unsafe in_spk_buf,
                                                   int * unsafe out_mic_buf, int * unsafe out_spk_buf):
                    in_mic = in_mic_buf;
                    in_spk = in_spk_buf;
                    out_mic = out_mic_buf;
                    out_spk = out_spk_buf;
                        
                    process_block = 1;
                    break;


                process_block => default:

                    process_block = 0;
                    // Loopback the blocks without processing
                    for(int i = 0; i < BLOCK_SIZE; i++) 
                    {
                        *(out_mic + i) = *(in_mic + i * NUM_MIC_INPUTS);
                        *(out_spk + i) = *(in_spk + i);
                    }
                    break;
            }
        }
    }
}


