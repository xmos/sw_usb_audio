#include <platform.h>

/* This is provided as simple example but disabled due to the port clash with audiostream.xc */

#if 0
on tile[0]: out port p_leds = XS1_PORT_4F;

void UserHostActive(int active)
{
    if(active)
    {
        /* Turn all LEDs on */
        p_leds <: 0xF;
    }
    else
    {
        /* Turn all LEDs off */
        p_leds <: 0x0;
    }
}
#endif
