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
