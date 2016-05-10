#ifdef XVSM
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <xclib.h>
#include <stdint.h>
#include "devicedefines.h"
#include "xua_dsp.h"
#include "print.h"
#include "xvsm_support.h"
#include "usr_dsp_cmd.h"

/* DSP data double buffered */
int dspBuffer_in_adc[2][ILV_FRAMESIZE * ILV_NCHAN_MIC_IN]; 
int dspBuffer_in_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_dac[2][ILV_FRAMESIZE]; 

unsigned g_loopback = 0;
unsafe
{
    unsigned * unsafe loopback = &g_loopback;
}

/* sampsFromUsbToAudio: The sample frame the device has recived from the host and is going to play to the output audio interfaces */
/* sampsFromAudioToUsb: The sample frame that was received from the audio interfaces and that the device is going to send to the host */
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[], client dsp_if i_dsp)
{
    static unsigned dspSampleCount = 0;
    static unsigned dspBufferNo = 0;
    
    /* Add samples to DSP buffers */
    dspBuffer_in_adc[dspBufferNo][(dspSampleCount * ILV_NCHAN_MIC_IN)+1] = sampsFromAudioToUsb[PDM_MIC_INDEX]*12;
    dspBuffer_in_adc[dspBufferNo][(dspSampleCount * ILV_NCHAN_MIC_IN)] = sampsFromAudioToUsb[PDM_MIC_INDEX+1]*12;
    dspBuffer_in_usb[dspBufferNo][dspSampleCount] = sampsFromUsbToAudio[0];
 
    unsafe
    { 
        if(*loopback)
        {
            /* Read out of DSP buffer */
            sampsFromUsbToAudio[0] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];
            sampsFromUsbToAudio[1] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];
        }
    }
    
    /* Read out of DSP buffer */
    sampsFromAudioToUsb[0] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];
    sampsFromAudioToUsb[1] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];

    dspSampleCount++; 
   if(dspSampleCount >= ILV_FRAMESIZE)
    unsafe{
        i_dsp.transfer_buffers((int * unsafe) dspBuffer_in_adc[dspBufferNo], (int * unsafe) dspBuffer_in_usb[dspBufferNo], 
                                    (int * unsafe) dspBuffer_out_usb[dspBufferNo], (int * unsafe) dspBuffer_out_dac[dspBufferNo]);
        dspSampleCount = 0;
        dspBufferNo = 1 - dspBufferNo;
    }
} 

#pragma unsafe arrays
void dsp_process(server dsp_if i_dsp, server dsp_ctrl_if i_dsp_ctrl[numDspCtrlInts], unsigned numDspCtrlInts)
{
    il_voice_cfg_t          ilv_cfg;
    il_voice_rtcfg_t        ilv_rtcfg;
    il_voice_diagnostics_t  ilv_diag;

    int * unsafe in_mic = NULL, * unsafe in_spk = NULL;
    int * unsafe out_mic = NULL, * unsafe out_spk = NULL;
    
    int processingBlock = 0;
    int fullBypass = 0;
    int err;

    /* Initialize config structures to viable default values */
    il_voice_get_default_cfg(ilv_cfg, ilv_rtcfg);   

    /* Setup parameters in config structure */
    ilv_rtcfg.agc_on = 1;
    ilv_rtcfg.aec_on = 0;
    ilv_rtcfg.rvb_on = 1;
    ilv_rtcfg.bypass_on = 0;
    ilv_rtcfg.bf_on = 1;
    
    /* Initialize XSVSM block */
    err = il_voice_init(ilv_cfg, ilv_rtcfg);

    unsafe 
    {
        while(1)
        {
            select
            {
                case i_dsp_ctrl[int ctrlInt].setControl(unsigned cmd, unsigned offset, unsigned value) -> int handled:

                    switch(cmd)
                    {
                        case CMD_DSP_RTCFG:
                            char * base;
                            base = (char *) &ilv_rtcfg;
                            *(base+offset) = value;
                            break;
                        case CMD_DSP_FULLBYPASS:
                            fullBypass = value;
                            break;
                        case CMD_DSP_LOOPBACK:
                            *loopback = value;
                            break;
                        default:
                            break;
                    }
                    if((err = il_voice_update_cfg(ilv_rtcfg)) != 0)
                    {
                        printstr("cntrlAudioProcess:: ERROR il_voice_update_cfg(). Error Code = "); printintln(err);
                    }
                    handled = 1;
                    
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

                /* Guarded default case */
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
                        for(int i = 0; i < ILV_FRAMESIZE; i++) 
                        {
                            *(out_mic + i) = *(in_mic + i * ILV_NCHAN_MIC_IN);
                            *(out_spk + i) = *(in_spk + i);
                        }
                    }
                    break;
            }
        }
    }
}
#endif
