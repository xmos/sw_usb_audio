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

#include "xassert.h"
#include "control_module_ids.h"
#include <stdlib.h>

#if CONTROL
#include "stdio.h"
#warning "DEV using stdio/printf - remove me"
#endif

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

[[combinable]]
void xscope_server(chanend c_xscope, client interface control i_modules[1])
{
  uint8_t bytes[512];
  int num_bytes_read;
  size_t return_size;

  xscope_connect_data_from_host(c_xscope);


  while (1) {
    select {
      /* tools_xtrace/xscope_api/xcore_shared/xscope_shared_xc.xc */
      case xscope_data_from_host(c_xscope, bytes, num_bytes_read):
        assert(num_bytes_read <= sizeof(bytes));

        //For the old demo, we want to pass the raw data across
        //control_handle_message_xscope(bytes, return_size, i_modules, 1);
        i_modules[0].set(0, num_bytes_read, bytes);
        if (return_size > 0) {
          //xscope_core_bytes(0, return_size, bytes);
        }
        /* xTAG adapter should defer further calls by NAKing USB transactions */
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
