
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <xclib.h>
#include <stdint.h>
#include "dsp.h"
#include "print.h"
#include "il_voice.h"

il_voice_cfg_t          ilv_cfg;
il_voice_rtcfg_t        ilv_rtcfg;
il_voice_diagnostics_t  ilv_diag;

//TODO
#define NUM_MIC_INPUTS 2
#define BLOCK_SIZE 160

void dsp_process(server dsp_if i_dsp, server dsp_ctrl_if ?i_dsp_ctrl[numDspCtrlInts], unsigned numDspCtrlInts)
{
    int * unsafe in_mic = NULL, * unsafe in_spk = NULL;
    int * unsafe out_mic = NULL, * unsafe out_spk = NULL;
    
    int processingBlock = 0;
    int fullBypass = 0;
    int err;
    unsigned char oldButtonVal = 0;

    /* Initialize config structures to viable default values */
    il_voice_get_default_cfg(ilv_cfg, ilv_rtcfg);   

    /* Setup parameters in config structure */
    ilv_rtcfg.agc_on = 1;
    ilv_rtcfg.aec_on = 0;
    ilv_rtcfg.rvb_on = 1;
    ilv_rtcfg.bypass_on = 1;
    ilv_rtcfg.bf_on = 1;
    
    /* Initialize XSVSM block */
    err = il_voice_init(ilv_cfg, ilv_rtcfg);

    unsafe 
    {
        while(1)
        {
            select
            {
                case i_dsp_ctrl[int ctrlInt].setControl(unsigned offset, unsigned value, unsigned unused) -> int handled:

                    printintln(ilv_rtcfg.bypass_on);
                    char * base;
                    base = (char *) &ilv_rtcfg;
                    *(base+offset) = value;

                    printintln(ilv_rtcfg.bypass_on);

                    if(il_voice_update_cfg(ilv_rtcfg))
                    {
                        printstr("cntrlAudioProcess:: ERROR il_voice_update_cfg(). Error Code = "); printintln(err);
                    }
                    
                    break;
            
                /* Client wants a processed block. Also gives us input samples */
                case !processingBlock => i_dsp.transfer_buffers(int * unsafe in_mic_buf, int * unsafe in_spk_buf,
                                                   int * unsafe out_mic_buf, int * unsafe out_spk_buf):
                    in_mic = in_mic_buf;
                    in_spk = in_spk_buf;
                    out_mic = out_mic_buf;
                    out_spk = out_spk_buf;
                    processingBlock = 1;
                    break;


                processingBlock => default:

                    processingBlock = 0;
            
                    if(!fullBypass)
                    {
                        il_voice_process((int *) in_mic, (int *) in_spk, (int *) out_mic, (int *) out_spk);
                            
                        il_voice_get_diagnostics(ilv_diag);

                    }
                    else
                    {
                        /* Loopback the blocks without processing */
                        for(int i = 0; i < BLOCK_SIZE; i++) 
                        {
                            *(out_mic + i) = *(in_mic + i * NUM_MIC_INPUTS);
                            *(out_spk + i) = *(in_spk + i);
                        }
                    }
                    break;
            }
        }
    }
}


