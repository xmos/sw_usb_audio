// Copyright (c) 2016, XMOS Ltd, All rights reserved
#ifdef HARDWARE
#include <xs1.h>
#include "gpio_access.h"

void p_gpio_lock()
{
}

void p_gpio_unlock()
{
}

unsigned p_gpio_peek()
{
    unsigned portId, x;

    asm("ldw %0, dp[p_gpio]":"=r"(portId));
    asm volatile("peek %0, res[%1]":"=r"(x):"r"(portId));

    return x;
}

void p_gpio_out(unsigned x)
{
    unsigned portId;

    asm("ldw %0, dp[p_gpio]":"=r"(portId));
    asm volatile("out res[%0], %1"::"r"(portId),"r"(x));
}

void set_gpio(unsigned bit, unsigned value)
{
	unsigned port_shadow;
	port_shadow = p_gpio_peek();         // Read port pin value
	if (value == 0) port_shadow &= ~bit; // If writing a 0, generate mask and AND with current val
	else port_shadow |= bit;             // Else use mask and OR to set bit
	p_gpio_out(port_shadow);             // Write back to port. Will make port an output if not already
}

#endif
