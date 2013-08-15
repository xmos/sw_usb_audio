#include <xs1.h>
#include "devicedefines.h"
#include "gpio_defines.h"

void UserHostActive(int active)
{
    unsigned x;
    
    if(active)
    {
        asm volatile("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A)); 
        
        x |= P_GPIO_LEDA;

        asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x)); 
    }
    else
    {
        asm volatile("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A)); 
        
        x &= (~P_GPIO_LEDA);

        asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x)); 
    }
}


