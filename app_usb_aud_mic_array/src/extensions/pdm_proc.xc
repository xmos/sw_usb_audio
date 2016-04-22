
#include "customdefines.h"
#include <platform.h>
#include <xs1.h>
#include <stdio.h>
#include "mic_array.h"
#include "xua_pdm_mic.h"
#include <print.h>

/** Structure to describe the LED ports*/
typedef struct {
    out port p_led0to7;     /**<LED 0 to 7. */
    out port p_led8;        /**<LED 8. */
    out port p_led9;        /**<LED 9. */
    out port p_led10to12;   /**<LED 10 to 12. */
    out port p_leds_oen;    /**<LED Output enable (active low). */
} led_ports_t;


#define LED_COUNT 13
#define BUTTON_PORTS  PORT_BUT_A_TO_D
#define LED_PORTS     {PORT_LED0_TO_7, PORT_LED8, PORT_LED9, PORT_LED10_TO_12, PORT_LED_OEN}

on tile[0] : in port p_buttons     = BUTTON_PORTS;
on tile[0] : led_ports_t leds      = LED_PORTS;

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

/* Offsetof currently only provided for C/C++ */
#define myoffsetof(st, m) \
        ((size_t) ( (char * unsafe)&((st * unsafe)(0))->m - (char * unsafe)0 ))

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


#ifdef PDM_PROC_SIMPLE

/* Most basic processing example */
#ifndef MIC_PROCESSING_USE_INTERACE
void user_pdm_init()
{
    /* do nothing */
}
#endif

#ifdef MIC_PROCESSING_USE_INTERFACE
[[combinable]]
void user_pdm_process(server mic_process_if i_mic_data)
#else
void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
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
            unsafe{
                /* Simply copy input buffer to output buffer unmodified */
                output[i] += audio->data[i][0];
            }
#ifdef MIC_PROCESSING_USE_INTERFACE
            break;
        } // select{}
    }  // while(1)
#endif
}





#elif PDM_PROC_SUMMING
void user_pdm_init()
{

    /* Turn center LED on */
    for(int i = 0; i < 12; i++)
        set_led(i, 0);

    set_led(12, 255);
    
    leds.p_leds_oen <: 1;
    leds.p_leds_oen <: 0;
}

#define BUTTON_COUNT 1000

#ifdef MIC_PROCESSING_USE_INTERFACE
[[combinable]]
void user_pdm_process(server mic_process_if i_mic_data)
{
    /* Very simple button control code for example */
    unsigned count = 0;
    unsigned oldButtonVal = 0;
    unsigned summed = 0;
    unsigned gain = 1;
#else
void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
    /* Very simple button control code for example */
    static unsigned count = 0;
    static unsigned oldButtonVal = 0;
    static unsigned summed = 0;
    static unsigned gain = 1;
#endif
  
#ifdef MIC_PROCESSING_USE_INTERFACE
while(1)
{
select
{
    case i_mic_data.init():
        user_pdm_init();
        break;

    case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio, int output[]):
#endif

    count++;
    if(count == BUTTON_COUNT)
    {
        count = 0;
        unsigned char buttonVal;
        p_buttons :> buttonVal;

        if(oldButtonVal != buttonVal)
        {
            switch (buttonVal)  
            {
                case 0xE:  /* Button A */

                    summed = !summed;
                
                    if(summed)  
                    {
                        for(int i = 0; i < 13; i++)
                            set_led(i, 255);
                    }
                    else
                    {
                         /* Keep center LED on */
                         for(int i = 0; i < 12; i++)
                            set_led(i, 0);
                    }
                    break;

                case 0xD:  /* Button B */
                    gain++;
                    printf("Gain Up: %d\n", gain);
                    break;

                case 0xB:  /* Button C */
                    gain--;
                    if(gain < 0)
                        gain = 0;
                    printf("Gain Down: %d\n", gain);
                    break;

                case 0x7:  /* Button D */
                    break;
            }
            oldButtonVal = buttonVal;
        }
    }

    if(summed)
    {
        
        /* Sum up all the mics */
        output[0] = 0;
        for(unsigned i=0; i<7; i++)
        unsafe{
            output[0] += audio->data[i][0];
        }

        /* Apply gain to sum */
        output[0] *= gain;

        /* Apply gain to individual mics */
        for(unsigned i=0; i<7; i++)
        unsafe{
            int x = audio->data[i][0];
            x*=gain;
            output[i+1] = x;
        }
    }
    else
    {
        /* Send individual mics (with gain applied) */        
        for(unsigned i=0; i<7; i++)
        unsafe{
            int x = audio->data[i][0];
            x *=gain;
            output[i] = x;
        }
    }

#ifdef MIC_PROCESSING_USE_INTERFACE
    break;
    }// select{}
}// while(1)
#endif
}



#else


#include "usr_dsp_cmd.h"
#include "xvsm_support.h"
#include "lib_voice_doa_naive.h"

/* Global processing state */
unsigned g_doDoa = 0;
unsigned char g_micNum = 1;
unsigned g_processingBypassed = 0;
unsafe
{
    unsigned * unsafe doDoa = &g_doDoa;
    unsigned char * unsafe micNum = &g_micNum;
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

#ifdef MIC_PROCESSING_USE_INTERFACE
[[combinable]]
void user_pdm_process(server mic_process_if i_mic_data)
{
    lib_voice_doa_naive_init(doaState);

#else
void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
#endif
#ifdef MIC_PROCESSING_USE_INTERFACE
    /* Turn center LED on */
    for(int i = 0; i < 12; i++)
        set_led(i, 0);

    set_led(12, 255);
    
    /* Enable LED's */
    leds.p_leds_oen <: 1;
    leds.p_leds_oen <: 0;

    while(1)
    {
        select
        {
            case i_mic_data.init():
                break;

            case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio, int output[]):
#endif
           
            /* Light the LEDs */
            /* TODO ideally we don't want to do this every processing loop */
            unsafe
            { 
                for(int i = 1; i < 7; i++)
                {
                    if((i == *micNum) && !(*processingBypassed))
                        SetMicLeds(i, 255); 
                    else
                        SetMicLeds(i, 0); 
                }
                
                for(unsigned i=0; i<8; i++)
                {
                    /* Simply copy input buffer to output buffer unmodified */
                    output[i] = audio->data[i][0];
                }
                
                if(*doDoa)
                {   
                    int doaDir =  lib_voice_doa_naive_incorporate(doaState, output[1], output[2], output[3], output[4], 
                        output[5], output[6]);

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
