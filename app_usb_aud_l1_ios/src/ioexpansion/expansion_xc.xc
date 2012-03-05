#include <platform.h>
#include <print.h>
#include "xc_ptr.h"
#include "expansion.h"

/*
Bit Function
3   EXP_CLK
4   EXP_LATCH
5   EXP_OE_N
6   EXP_DATA
*/

#define P32A_EXP_CLK    0x08
#define P32A_EXP_LATCH  0x10
#define P32A_EXP_OE_N   0x20
#define P32A_EXP_DATA   0x40

unsigned g_oe_n = P32A_EXP_OE_N;
unsigned expansion_io_byte(int data_out, port exp_if)
{
    unsigned time;
    int portval = 0;
    unsigned data_in = 0;
    int tmp;
    expansion_o_byte(data_out, exp_if);
    // At this point portval should be (OE low, LATCH high, CLK high, DATA high)
    // Mock up portval to look like that.
    portval = (P32A_EXP_LATCH | P32A_EXP_CLK | P32A_EXP_DATA);

    // Get first bit from input shift reg (Bit 7).
    exp_if :> void @ time; // turn port around, throw away initial input
    time += 10; // Wait 100ns for shift reg to drive line through 4k7 resistor.
    exp_if @ time :> tmp; // get data input
    exp_if <: portval; // Turn port around
    data_in |= ((tmp & P32A_EXP_DATA) >> 6) << 7;
    
    // Now shift input data in from input shift reg.
    time += 10; // Make sure enough time to setup for loop
    for(int i = 6; i >= 0; i--) { // Get bits [6:0]
        time += 20; // Wait 20
        exp_if @ time <: (portval &= ~P32A_EXP_CLK); // Put CLK low
        time += 10;
        exp_if @ time <: (portval |= P32A_EXP_CLK); // Set clock high after 10
        time += 10;
        exp_if @ time :> void; // turn port around, throw away initial input
        time += 10; // Wait 100ns for shift reg to drive line through 4k7 resistor.
        exp_if @ time :> tmp; // get data input
        exp_if <: portval; // Turn port around
        data_in |= ((tmp & P32A_EXP_DATA) >> 6) << i;
    }
    return data_in;
}

void expansion_o_byte(int data_out, port exp_if)
{
    unsigned time;
    int portval = 0;
    unsigned oe_n;
    GET_SHARED_GLOBAL(oe_n, g_oe_n);
    
    // First, shift output data into output shift reg.
    
    exp_if <: (oe_n | P32A_EXP_CLK | P32A_EXP_LATCH | P32A_EXP_DATA) @ time; // Everything high apart from OE_N
    time += 10; // Make sure enough time to setup for loop
    for(int i = 7; i >= 0; i--) { // Get bits [7:0]
        time += 10; // Wait 10
        // assemble output word
        portval = (oe_n | ((data_out >> i & 0x1) << 6) | P32A_EXP_LATCH); // DATA bit, OE_N low, LATCH high, CLK low
        exp_if @ time <: portval; // output portval at time
        time += 10;
        exp_if @ time <: (portval |= P32A_EXP_CLK); // Set clock high after 10
    }

    // Now, Latch shift register output onto output pins, this will simultaneously sample input pins of input shift reg.
    time += 10;
    exp_if @ time <: (portval &= ~P32A_EXP_LATCH); // Set Latch low
    time += 10;
    exp_if @ time <: (portval |= (P32A_EXP_DATA | P32A_EXP_LATCH)); // Set Data and Latch high
    time += 10;
    
    // Set output enable now we have sensible values in SR and latched
    oe_n = 0; // set for next time around
    SET_SHARED_GLOBAL(g_oe_n, oe_n);
    portval &= ~P32A_EXP_OE_N; // and set low for this time
    exp_if @ time <: portval; // Drive OE_N low
}
