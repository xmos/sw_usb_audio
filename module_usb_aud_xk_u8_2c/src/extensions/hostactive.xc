#include <xs1.h>
#include "devicedefines.h"
#include "gpio_defines.h"
#include "gpio_access.h"

void UserHostActive(int active)
{
    unsigned x;
    
    if(active)
    {
        port32A_peek(x);
        
        x |= P_GPIO_LEDA;

        port32A_out(x);
    }
    else
    {
        port32A_peek(x);
        
        x &= (~P_GPIO_LEDA);

        port32A_out(x);
    }
}


