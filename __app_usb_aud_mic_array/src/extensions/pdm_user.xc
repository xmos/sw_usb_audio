
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include "mic_array.h"

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
on tile[0] : led_ports_t leds = LED_PORTS;

unsigned gain = 1;

void set_led_brightness(unsigned ledNo, unsigned ledVal)
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

#define BUTTON_COUNT 1000

unsigned summed = 0;

void user_pdm_init()
{

    /* Turn center LED on */
    for(int i = 0; i < 12; i++)
        set_led_brightness(i, 0);

    set_led_brightness(12, 255);
    
    leds.p_leds_oen <: 1;
    leds.p_leds_oen <: 0;
}

unsafe void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
    /* Very simple button control code for example */
    static unsigned count = BUTTON_COUNT;
    static unsigned oldButtonVal = 0;
     
    count--;
    if(count == 0)
    {
        count = BUTTON_COUNT;
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
                            set_led_brightness(i, 255);
                    }
                    else
                    {
                         /* Keep center LED on */
                         for(int i = 0; i < 12; i++)
                            set_led_brightness(i, 0);
                    }
                    break;

                case 0xD:  /* Button B */
                    gain++;
                    printf("Gain Up: %d\n", gain);
                    break;

                case 0xB:  /* Button C */
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
        output[0] = 0;
        for(unsigned i=0; i<7; i++)
        {
            output[0] += audio->data[i][0];
        }

        /* Apply gain to sum */
        output[0] *= gain;

        /* Apply gain to individual mics */
        for(unsigned i=0; i<7; i++)
        {
            int x = audio->data[i][0];
            x*=gain;
            output[i+1] = x;
        }
    }
    else
    {
        /* Send individual mics (with gain applied) */        
        for(unsigned i=0; i<7; i++)
        {
            int x = audio->data[i][0];
            x *=gain;
            output[i] = x;
        }
    }
}

