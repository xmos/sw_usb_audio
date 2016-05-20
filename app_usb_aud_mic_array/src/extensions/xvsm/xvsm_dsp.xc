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

/** Structure to describe the LED ports*/
typedef struct {
    out port p_led0to7;     /**<LED 0 to 7. */
    out port p_led8;        /**<LED 8. */
    out port p_led9;        /**<LED 9. */
    out port p_led10to12;   /**<LED 10 to 12. */
    out port p_leds_oen;    /**<LED Output enable (active low). */
} led_ports_t;

#define LED_COUNT 13
#define LED_PORTS     {PORT_LED0_TO_7, PORT_LED8, PORT_LED9, PORT_LED10_TO_12, PORT_LED_OEN}

on tile[0] : led_ports_t leds      = LED_PORTS;

/* DSP data double buffered */
int dspBuffer_in_adc[2][ILV_FRAMESIZE * ILV_NCHAN_MIC_IN]; 
int dspBuffer_in_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_dac[2][ILV_FRAMESIZE]; 

unsigned g_loopback = 0;
    
unsafe
{
   extern unsigned char * unsafe micNum;
}

unsafe
{
    unsigned * unsafe loopback = &g_loopback;
}

void set_led(unsigned ledNo, unsigned ledVal)
{
    static int ledVals[LED_COUNT] = {0};
   
    ledVals[ledNo] = ledVal;

    unsigned d = 0;
    for(int i = 0; i < 8; i++)
    {
        d |= ((ledVals[i] == 0) << i);
    }   
    leds.p_led0to7 <: d;
    leds.p_led8 <: (ledVals[8] == 0);
    leds.p_led9 <: (ledVals[9] == 0);
 
    d = 0;
    for(int i = 10; i < 13; i++)
    {
        d |= ((ledVals[i] == 0) << (i-10));
    }         
    leds.p_led10to12 <: d;
}

void SetMicLeds(int micNum, int val)
{
    int ledNum1 = micNum*2-2;
    int ledNum2 = micNum*2-1;

    if(ledNum2 < 0)
        ledNum2 = 11;
    
    if(ledNum1 < 0)
        ledNum1 = 11;

    set_led(ledNum1, val);
    set_led(ledNum2, val);
}






/* sampsFromUsbToAudio: The sample frame the device has recived from the host and is going to play to the output audio interfaces */
/* sampsFromAudioToUsb: The sample frame that was received from the audio interfaces and that the device is going to send to the host */
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[], client audManage_if i_audMan)
{
    int dspBuffer_in_adc2[2];
    int dspBuffer_in_usb2[1]; // TODO rename
    int dspBuffer_out_usb2[1]; // TODO rename
    int dspBuffer_out_dac2[1]; // TODO rename

    dspBuffer_in_adc2[0] = sampsFromAudioToUsb[PDM_MIC_INDEX];
    dspBuffer_in_adc2[1] = sampsFromAudioToUsb[PDM_MIC_INDEX+1];
    dspBuffer_in_usb2[0] = sampsFromUsbToAudio[0];
    
    i_audMan.transfer_samples(dspBuffer_in_adc2, dspBuffer_in_usb2, dspBuffer_out_usb2, dspBuffer_out_dac2);
   
    /* Read out of DSP buffer */
    sampsFromAudioToUsb[0] = dspBuffer_out_usb2[0];
    sampsFromAudioToUsb[1] = dspBuffer_out_usb2[0];
} 

/* TODO This task could be combined */
void dsp_buff(server audManage_if i_audMan, client dsp_if i_dsp)
{
    unsigned dspBufferNo = 0;
    unsigned dspSampleCount = 0;
    while(1)
    {
        select
        {
            case i_audMan.transfer_samples(int in_mic_buf[], int in_spk_buf[], int out_mic_buf[], int out_spk_buf[]):
                 
                /* Add samples to DSP buffers */
                dspBuffer_in_adc[dspBufferNo][(dspSampleCount * ILV_NCHAN_MIC_IN)+1] = in_mic_buf[0];
                dspBuffer_in_adc[dspBufferNo][(dspSampleCount * ILV_NCHAN_MIC_IN)] = in_mic_buf[1];
                dspBuffer_in_usb[dspBufferNo][dspSampleCount] = in_spk_buf[0];

                /* Read out of DSP buffer */
                out_mic_buf[0] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];
                out_mic_buf[1] = dspBuffer_out_usb[dspBufferNo][dspSampleCount];

                dspSampleCount++; 
                if(dspSampleCount >= ILV_FRAMESIZE)
                unsafe{
                    dspSampleCount = 0;
                    dspBufferNo = 1 - dspBufferNo;  
                    
                    i_dsp.transfer_buffers((int * unsafe) dspBuffer_in_adc[dspBufferNo], (int * unsafe) dspBuffer_in_usb[dspBufferNo], 
                                    (int * unsafe) dspBuffer_out_usb[dspBufferNo], (int * unsafe) dspBuffer_out_dac[dspBufferNo]);
                }
             
                break; 
        }
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

    /* Turn center LED on */
    for(int i = 0; i < 12; i++)
        set_led(i, 0);

    set_led(12, 255);
    
    /* Enable LED's */
    leds.p_leds_oen <: 1;
    leds.p_leds_oen <: 0;

    /* Initialize config structures to viable default values */
    il_voice_get_default_cfg(ilv_cfg, ilv_rtcfg);   

    /* Setup parameters in config structure */
    ilv_rtcfg.agc_on = 1;
    ilv_rtcfg.aec_on = 1;
    ilv_rtcfg.rvb_on = 1;
    ilv_rtcfg.ns_on = 1;
    ilv_rtcfg.bypass_on = 0;
    ilv_rtcfg.bf_on = 1;
    ilv_rtcfg.mic_shift = 2; 
    
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

                        for(int i = 1; i < 7; i++)
                        unsafe
                        {
                            if(i == *micNum) 
                                SetMicLeds(i, 255); 
                            else
                                SetMicLeds(i, 0); 
                        }
                    }
                    else
                    {
                        SetMicLeds(*micNum, 0);            

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
