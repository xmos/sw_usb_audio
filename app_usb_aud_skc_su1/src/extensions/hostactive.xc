

#include <xs1.h>
#include "devicedefines.h"

#include "p_gpio.h"
#include "p_gpio_defines.h"

void UserHostActive(int active)
{
    /* Kill the steam active LED on an unplug - important if we are self-powered */
    if(!active)
    {
        int x;

        x = p_gpio_peek();
        x &= (~P_GPIO_LED);
        p_gpio_out(x);
    }
}


