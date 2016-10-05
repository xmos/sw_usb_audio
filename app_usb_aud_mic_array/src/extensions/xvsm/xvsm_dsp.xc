#ifdef XVSM
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <xclib.h>
#include <stdint.h>

#include "devicedefines.h"
#include "xvsm_dsp.h"
#include "print.h"
#include "xvsm_support.h"
#include "usr_dsp_cmd.h"  //TODO required?
#include "control.h"
#include "control_ids.h"

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

#define BUTTON_PORTS  PORT_BUT_A_TO_D
on tile[0] : in port p_buttons     = BUTTON_PORTS;

/* DSP data double buffered */
int dspBuffer_in_adc[2][ILV_FRAMESIZE * ILV_NCHAN_MIC_IN]; 
int dspBuffer_in_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_usb[2][ILV_FRAMESIZE]; 
int dspBuffer_out_dac[2][ILV_FRAMESIZE]; 

/* Global DSP state/settings */
unsigned g_doDoa = 0;
unsigned char g_micNum = 1;
unsigned g_procBypassed = 0;
unsigned g_loopback = 0;

unsafe
{
    unsigned char * unsafe micNum = &g_micNum;
    unsigned * unsafe doDoa = &g_doDoa;
    unsigned * unsafe procBypassed = &g_procBypassed;
    unsigned * unsafe loopback = &g_loopback;
}

void SetLed(unsigned ledNo, unsigned ledVal)
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

    SetLed(ledNum1, val);
    SetLed(ledNum2, val);
}

[[combinable]]
void dsp_control(/*client dsp_ctrl_if i_dsp_ctrl*/)
{
    int buttonVal;
    p_buttons :> buttonVal;
    timer t;
    unsigned time;
    int debouncing = 0;

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
                        *procBypassed = !(*procBypassed);

                        if(*procBypassed)
                            printstr("Processing bypassed\n");
                        else
                            printstr("Processing active\n");
                        
                        break;
                    }  

                    case 0xD: /* Button B */
                    unsafe
                    { 
                        *loopback = !(*loopback);
                        if(*loopback)
                            printstr("Loopback enabled\n");
                        else
                            printstr("Loopback disabled\n");
                        break;
                    }

                    case 0xB: /* Button C */
                    unsafe
                    { 
                        if(!*procBypassed)
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


/* sampsFromUsbToAudio: The sample frame the device has recived from the host and is going to play to the output audio interfaces */
/* sampsFromAudioToUsb: The sample frame that was received from the audio interfaces and that the device is going to send to the host */
/* Note: this is called from audio_io() */
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[], client audManage_if i_audMan)
{
    int dspBuffer_in_adc_local[2];
    int dspBuffer_in_usb_local[1]; 
    int dspBuffer_out_usb_local[1]; 
    int dspBuffer_out_dac_local[1];

    dspBuffer_in_adc_local[0] = sampsFromAudioToUsb[PDM_MIC_INDEX];
    dspBuffer_in_adc_local[1] = sampsFromAudioToUsb[PDM_MIC_INDEX+1];
    dspBuffer_in_usb_local[0] = sampsFromUsbToAudio[0];
    
    i_audMan.transfer_samples(dspBuffer_in_adc_local, dspBuffer_in_usb_local, dspBuffer_out_usb_local, dspBuffer_out_dac_local);
   
#ifndef XVSM_TEST
    /* Read out of DSP buffer - samples for USB */
    sampsFromAudioToUsb[0] = dspBuffer_out_usb_local[0];
    sampsFromAudioToUsb[1] = dspBuffer_out_usb_local[0];
#else

    sampsFromAudioToUsb[0] = sampsFromAudioToUsb[PDM_MIC_INDEX];     // Mic In 0
    sampsFromAudioToUsb[1] = sampsFromAudioToUsb[PDM_MIC_INDEX+1];   // Mic In 1
    sampsFromAudioToUsb[2] = sampsFromUsbToAudio[0];                 // Spk In
    sampsFromAudioToUsb[3] = dspBuffer_out_usb_local[0];             // Mic Out
    sampsFromAudioToUsb[4] = dspBuffer_out_dac_local[0];             // Spk Out
    sampsFromAudioToUsb[5] = 0x7fffffff;                             // Spare
#endif

    /* Read out of DSP buffer - samples for I2S */
    sampsFromUsbToAudio[0] = dspBuffer_out_dac_local[0];
    sampsFromUsbToAudio[1] = dspBuffer_out_dac_local[0];
} 

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

                unsafe
                {
                    if(*loopback)
                    {
                        out_spk_buf[0] = dspBuffer_out_usb[dspBufferNo][dspSampleCount]; 
                    }
                    else
                    {
                        out_spk_buf[0] = dspBuffer_out_dac[dspBufferNo][dspSampleCount]; 
                    }
                }   


                dspSampleCount++; 
                if(dspSampleCount >= ILV_FRAMESIZE)
                unsafe{
                    
                    i_dsp.transfer_buffers((int * unsafe) dspBuffer_in_adc[dspBufferNo], (int * unsafe) dspBuffer_in_usb[dspBufferNo], 
                                    (int * unsafe) dspBuffer_out_usb[dspBufferNo], (int * unsafe) dspBuffer_out_dac[dspBufferNo]);
               
                    dspSampleCount = 0;
                    dspBufferNo = 1 - dspBufferNo;  
                }
                break; 
        }
    }
}


static unsigned g_vadThresh_detectTime = 2;
static unsigned g_vadThresh_entry = 4000;
static unsigned g_vadThresh_cont = 2000;
static unsigned g_vadTimeout = 50;
vadState_t g_vadState = VAD_IDLE;

unsafe
{
    vadState_t * unsafe vadState = &g_vadState;
}

int cntrlAudioProcess(il_voice_rtcfg_t &ilv_rtcfg, il_voice_cfg_t &ilv_cfg, il_voice_diagnostics_t &ilv_diag,
  control_resid_t res, control_cmd_t cmd, int &param, int baseResId);


/* TODO this needs to be called on reset */
void il_voice_get_default_cfg_xmos(il_voice_cfg_t &ilv_cfg, il_voice_rtcfg_t &ilv_rtcfg)
{
    /* Initialize config structures to viable default values */
    il_voice_get_default_cfg(ilv_cfg, ilv_rtcfg);   

    /* Setup parameters in config structure */
    ilv_rtcfg.agc_on = 1;
    ilv_rtcfg.aec_on = 1;
    ilv_rtcfg.rvb_on = 1;
    ilv_rtcfg.ns_on = 1;
    ilv_rtcfg.bypass_on = 0;
    ilv_rtcfg.bf_on = 1;
    ilv_rtcfg.mic_shift = 4;
}

#pragma unsafe arrays
void dsp_process(server dsp_if i_dsp, server interface control i_control, const size_t num_modules)
{
    il_voice_cfg_t          ilv_cfg;
    il_voice_rtcfg_t        ilv_rtcfg;
    il_voice_diagnostics_t  ilv_diag;
    
    int * unsafe in_mic = NULL, * unsafe in_spk = NULL;
    int * unsafe out_mic = NULL, * unsafe out_spk = NULL;
    
    int processingBlock = 0;
    int err;

    int vadTimeout = 0;
    int vadDetectTime = 0;

    /* Turn center LED on */
    for(int i = 0; i < 12; i++)
        SetLed(i, 0);

    SetLed(12, 255);
    
    /* Enable LED's */
    leds.p_leds_oen <: 1;
    leds.p_leds_oen <: 0;

    /* Initialize config structures to viable default values */
    il_voice_get_default_cfg_xmos(ilv_cfg, ilv_rtcfg);   

    ilv_cfg.spk_eq = NULL;
    ilv_cfg.mic_eq = NULL;

    /* Initialize XSVSM block */
    err = il_voice_init(ilv_cfg, ilv_rtcfg);

    unsafe 
    {
        while(1)
        {
            select
            {
#if 0
                case i_dsp_ctrl[int ctrlInt].setControl(unsigned cmd, unsigned offset, unsigned value) -> int handled:

                    switch(cmd)
                    {
                        case CMD_DSP_RTCFG:
                            char * base;
                            base = (char *) &ilv_rtcfg;
                            *(base+offset) = value;
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
#endif     
                case i_control.register_resources(control_resid_t resources[MAX_RESOURCES_PER_INTERFACE], unsigned &num_resources):
                    unsigned i = 0;
                
                    /* XVSM resources */
                    for(int x = IVL_RESID_BASE; x < (IVL_RESID_BASE + IVL_RESID_COUNT); x++)
                    {
                        resources[i++] = x;
                    }
            
                    /* 
                    resources[i++] = IVL_BASE_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_INIT_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_BYPASS_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_MIC_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_BEAM_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_NOISE_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_DEREV_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_AEC_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_AGC_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_EQ_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_SPK_LIM_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_SPK_CMP_RESID + IVL_RESID_BASE;
                    resources[i++] = IVL_DIAG_RESID + IVL_RESID_BASE;
                    */

                    /* DOA resource(s) */
                    resources[i++] = DOA_RESID + DOA_RESID_BASE;

                    /* VAD resource(s) */
                    resources[i++] = VAD_RESID + VAD_RESID_BASE;
                    
                    num_resources = i;
                    break;

                case i_control.write_command(control_resid_t resId, control_cmd_t cmd, const uint8_t data[n], unsigned n) -> control_resid_t res:
                    res = CONTROL_SUCCESS;
                    
                    if (n != 4) 
                    {
                        res = CONTROL_ERROR;
                        break;
                    }
                    
                    if((resId >= IVL_RESID_BASE) && (resId < IVL_RESID_COUNT + IVL_RESID_BASE))
                    unsafe
                    {
                        int param = (data, int);
                        res = cntrlAudioProcess(ilv_rtcfg, ilv_cfg, ilv_diag, resId, cmd, param, IVL_RESID_BASE);
                    }
                    else if((resId >= DOA_RESID_BASE) && (resId < DOA_RESID_COUNT + DOA_RESID_BASE))
                    {
                        switch(cmd)
                        {
                            case DOA_CMD_EN:
                                *doDoa = (data, int);
                                break;
                            case DOA_CMD_DIR: 
                                unsigned char * unsafe micNum = &g_micNum;
                                *micNum = (data, int);
                                break;
                             default:
                                res = CONTROL_ERROR;
                                break;
                        }
                    }
                    else if((resId >= VAD_RESID_BASE) && (resId < VAD_RESID_COUNT + VAD_RESID_BASE))
                    {
                        switch(cmd)
                        {
                            case VAD_CMD_THRESH_ENT: 
                                g_vadThresh_entry = (data, unsigned);
                                break;
                            case VAD_CMD_THRESH_EXIT:
                                g_vadThresh_cont = (data, unsigned);
                                break;
                            case VAD_CMD_DETECT_TIME:
                                g_vadThresh_detectTime = (data, unsigned); 
                                break;
                            case VAD_CMD_TIMEOUT:
                                g_vadTimeout = (data, unsigned); 
                                break;
                             default:
                                res = CONTROL_ERROR;
                                break;
                        }
                    }



                    break;

                case i_control.read_command(control_resid_t resId, control_cmd_t cmd, uint8_t data[n], unsigned n) -> control_resid_t res:

                    res = CONTROL_SUCCESS;
                        if (n != 4)
                        {
                            res = CONTROL_ERROR;
                            break;
                        }

                        int param = 0;
                        if((resId >= IVL_RESID_BASE) && (resId < IVL_RESID_COUNT + IVL_RESID_BASE))
                        unsafe
                        {
                            res = cntrlAudioProcess(ilv_rtcfg, ilv_cfg, ilv_diag, resId, cmd, param, IVL_RESID_BASE);
                            (data, unsigned[])[0] = param;
                        }
                        else if((resId >= DOA_RESID_BASE) && (resId < DOA_RESID_COUNT + DOA_RESID_BASE))
                        { 
                            cmd &=0x7f;
                            switch(cmd)
                            {
                                case DOA_CMD_EN:
                                    data[0] = *doDoa;
                                    break;
                                case DOA_CMD_DIR: 
                                    unsigned char * unsafe micNum = &g_micNum;
                                    data[0] = *micNum;
                                    break;

                                default:
                                    res = CONTROL_ERROR;
                                    break;
                            }
                        }  
                        else if((resId >= VAD_RESID_BASE) && (resId < VAD_RESID_COUNT + VAD_RESID_BASE))
                        {
                            cmd &=0x7f;
                            switch(cmd)
                            {
                                case VAD_CMD_THRESH_ENT: 
                                    data[0] = 12;
                                    (data, unsigned) = g_vadThresh_entry;
                                    break;
                                case VAD_CMD_THRESH_EXIT:
                                    (data, unsigned) = g_vadThresh_cont;
                                    break;
                                case VAD_CMD_DETECT_TIME:
                                    (data, unsigned) = g_vadThresh_detectTime; 
                                    break;
                                case VAD_CMD_TIMEOUT:
                                    (data, unsigned) = g_vadTimeout; 
                                    break;
                                 default:
                                    res = CONTROL_ERROR;
                                    break;
                            }
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

                /* Guarded default case */
                processingBlock => default:

                    processingBlock = 0;
            
                    if(!(*procBypassed))
                    {
                        il_voice_process((int *) in_mic, (int *) in_spk, (int *) out_mic, (int *) out_spk);
                        il_voice_get_diagnostics(ilv_diag);

                        switch(*vadState)
                        {
                            case VAD_IDLE:
                                
                                if(ilv_diag.mic_out_vad > g_vadThresh_entry)
                                {
                                    *vadState = VAD_DETECT;
                                    vadDetectTime = g_vadThresh_detectTime;
                                }

                                break;
                            
                            case VAD_DETECT:

                                if(ilv_diag.mic_out_vad > g_vadThresh_entry)
                                {
                                    if(vadDetectTime == 0)
                                    {
                                        *vadState = VAD_INVOICE;
                                    } 
                                    else 
                                    {
                                        vadDetectTime--;
                                    }
                                }
                                else
                                {
                                    *vadState = VAD_IDLE;
                                    vadTimeout = g_vadTimeout;
                                }
                                break;

                            case VAD_INVOICE:
                                
                                if(ilv_diag.mic_out_vad > g_vadThresh_cont)
                                {
                                    *vadState = VAD_INVOICE;
                                }
                                else
                                {
                                    *vadState = VAD_TIMEOUT; 
                                    vadTimeout = g_vadTimeout;
                                }
                                break;

                            case VAD_TIMEOUT:
                                
                                if(ilv_diag.mic_out_vad > g_vadThresh_cont)
                                {
                                    *vadState = VAD_INVOICE;
                                }
                                
                                vadTimeout--;

                                if(vadTimeout == 0)
                                {
                                   *vadState = VAD_IDLE; 
                                }  

                                break;

                        }

                        SetLed(12, (*vadState == VAD_INVOICE) || (*vadState == VAD_TIMEOUT));

                        for(int i = 1; i < 7; i++)
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
