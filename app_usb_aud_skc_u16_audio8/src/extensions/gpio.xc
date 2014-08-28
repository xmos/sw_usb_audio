#include <platform.h>
#include <xs1.h>
#include "gpio.h"

#define VERIFY_I2C 1

void set_gpio(out port p_gpio, unsigned bit, unsigned value)
{
	unsigned port_shadow;
	port_shadow = peek(p_gpio);         //Read port pin value
	if (value == 0) port_shadow &= ~bit;//If writing a 0, generate mask and AND with current val
	else port_shadow |= bit;            //Else use mask and OR to set bit
	p_gpio <: port_shadow;              //Write back to port. Will make port an output if not already
}

void wait_us(int microseconds)
{
    timer t;
    int time;

    t :> time;
    t when timerafter (time + (microseconds * 100)) :> void;
}
