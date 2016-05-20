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


#define BUTTON_PORTS  PORT_BUT_A_TO_D
on tile[0] : in port p_buttons     = BUTTON_PORTS;

/* Global processing state */
unsigned g_doDoa = 1;
unsigned char g_micNum = 1;
unsigned g_processingBypassed = 0;
unsafe
{
    unsigned char * unsafe micNum = &g_micNum;
    unsigned * unsafe doDoa = &g_doDoa;
    unsigned * unsafe processingBypassed = &g_processingBypassed;
}

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl)
{
    int buttonVal;
    p_buttons :> buttonVal;
    timer t;
    unsigned time;
    int debouncing = 0;
    int loopback = 0;

    while(1)
    {
        select
        {
            case !debouncing => p_buttons when pinsneq(buttonVal) :> buttonVal:
            {
                t :> time;
                time += 1000000;
                debouncing = 1;
                switch(buttonVal)
                {
                    case 0xE: /* Button A */
                    unsafe
                    { 
                        *processingBypassed = !(*processingBypassed);

                        int handled = i_dsp_ctrl.setControl(CMD_DSP_FULLBYPASS, 0, *processingBypassed);
                       
                        if(*processingBypassed)
                            printstr("Processing bypassed\n");
                        else
                            printstr("Processing active\n");
                        
                        break;
                    }  

                    case 0xD: /* Button B */
                    unsafe
                    { 
                        loopback = !loopback;
                        int handled = i_dsp_ctrl.setControl(CMD_DSP_LOOPBACK, 0, loopback);
                        if(loopback)
                            printstr("Loopback enabled\n");
                        else
                            printstr("Loopback disabled\n");
                        break;
                    }

                    case 0xB: /* Button C */
                    unsafe
                    { 
                        if(!*processingBypassed)
                        {    /* Use tmp variable to avoid race */
                            unsigned char * unsafe micNum = &g_micNum;

                            unsigned char tmp = (*micNum)+1;
                            if(tmp == 7)
                                tmp = 1;
                            *micNum = tmp;
                        }
                        break;
                    }

                    case 0x7: /* Button D */
                    unsafe
                    {
                        *doDoa = !(*doDoa);
                        printstr("DOA status: ");printintln(*doDoa);
                        break;
                    }
                    default:
                        break;
                }
                break;
            }
            case debouncing => t  when timerafter(time) :> int _:
                debouncing = 0;
                break;

        }
    }
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
                 
                if(*doDoa)
                {   
                    int doaDir = lib_voice_doa_naive_incorporate(doaState, output[1], output[2], output[3], output[4], output[5], output[6]);

                    if(doaDir > 0)
                    {
                        *micNum = 6 - (doaDir / 60);
                    }
                    output[1] = audio->data[*micNum][0];
                }
            }

#ifdef MIC_PROCESSING_USE_INTERFACE
            break;
        } // select{}
    }  // while(1)
#endif
}    
#endif
