
#include "customdefines.h"
#include <platform.h>
#include <xs1.h>
#include <stdio.h>
#include "mic_array.h"
#include "xua_pdm_mic.h"
#include <print.h>

#if defined(PDM_PROC_SUMMING)
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
void user_pdm_process(mic_array_frame_time_domain * unsafe audio)
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

    case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio):
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
                    if(gain!=0)
                        gain--;
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
        int sum = 0;
        for(unsigned i=0; i < NUM_PDM_MICS; i++)
        unsafe{
            sum += audio->data[i][0];
        }

        /* Apply gain to sum */
        sum *= gain;

        /* Apply gain to individual mics */
        for(unsigned i=0; i<NUM_PDM_MICS; i++)
        unsafe{
            int x = audio->data[i][0];
            x*=gain;
            audio->data[i][0] = x;
        }
    }
    else
    {
        /* Send individual mics (with gain applied) */        
        for(unsigned i=0; i<NUM_PDM_MICS; i++)
        unsafe{
            int x = audio->data[i][0];
            x *=gain;
            audio->data[i][0] = x;
        }
    }

#ifdef MIC_PROCESSING_USE_INTERFACE
    break;
    }// select{}
}// while(1)
#endif
}

#else /* PDM_PROC_SUMMING */

/* Most basic processing example - does nothing */
/* No need to provide anything for non-interface verson - default implementation available with weak symbols */
#ifdef MIC_PROCESSING_USE_INTERFACE
[[combinable]]
void user_pdm_process(server mic_process_if i_mic_data)
{
    while(1)
    {
        select
        {
            case i_mic_data.init():
                /* Do nothing */
                break;

            case i_mic_data.transfer_buffers(mic_array_frame_time_domain * unsafe audio):
                for(unsigned i=0; i<NUM_PDM_MICS; i++)
                unsafe{
                    /* Do Nothing */
                }   
                break;
        } // select{}
    }  // while(1)
}
#endif

#endif
