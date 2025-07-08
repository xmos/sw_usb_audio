// Copyright 2022-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#include <platform.h>

on tile[0]: out port p_leds = XS1_PORT_4F;

void UserAudioStreamState(int inputActive, int outputActive)
{
    if(inputActive || outputActive)
    {
        /* Turn all LEDs on */
        p_leds <: 0xF;
    } else
    {
        /* Turn all LEDs off */
        p_leds <: 0x0;
    }
}

