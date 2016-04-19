
#include "customdefines.h"
#include <platform.h>
#include <xs1.h>
#include <stdio.h>
#include "mic_array.h"
#include "pcm_pdm_mic.h"
#include <print.h>
#include "xvsm_support.h"

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


/* Most basic processing example */
#ifndef MIC_PROCESSING_USE_INTERACE
void user_pdm_init()
{
    /* do nothing */
}
#endif

/* Offsetof currently only provided for C/C++ */
#define myoffsetof(st, m) \
        ((size_t) ( (char * unsafe)&((st * unsafe)(0))->m - (char * unsafe)0 ))

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl)
{
    int buttonVal, newButtonVal;
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
                time += 100000;
                debouncing = 1;
                switch(buttonVal)
                {
                    case 0xE:
                    unsafe
                    { 
                        int handled = i_dsp_ctrl.setControl(myoffsetof(il_voice_rtcfg_t, bypass_on)/sizeof(char *), XVSM_BYPASS_MODE_ON, 0);
                        printstr("BYPASS ON"); 
                        break;
                    }                    
                        
                    case 0xD: 
                    unsafe
                    {
                        int handled = i_dsp_ctrl.setControl(myoffsetof(il_voice_rtcfg_t, bypass_on)/sizeof(char *), XVSM_BYPASS_MODE_OFF, 0);
                        printstr("BYPASS OFF"); 
                        break;
                    }

                    default:
                        printhexln(buttonVal);
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


#ifdef MIC_PROCESSING_USE_INTERFACE
[[distributable]]
void user_pdm_process(server mic_process_if i_mic_data)
{
#else
void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
#endif
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
                for(unsigned i=0; i<8; i++)
                unsafe {
                    /* Simply copy input buffer to output buffer unmodified */
                    output[i] = audio->data[i][0];
                }

#ifdef MIC_PROCESSING_USE_INTERFACE
            break;
        } // select{}
    }  // while(1)
#endif
}

