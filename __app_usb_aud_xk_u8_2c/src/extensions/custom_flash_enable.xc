
#include <xs1.h>
#include "gpio_defines.h"

#define PORT32A_PEEK(X) {asm volatile("peek %0, res[%1]":"=r"(X):"r"(XS1_PORT_32A));}
#define PORT32A_OUT(X)  {asm volatile("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(X));}

/* Any code required to enable SPI flash access */
void DFUCustomFlashEnable()
{
    int x;

    PORT32A_PEEK(x);
    x &= (~P_GPIO_SS_EN_CTRL);
    PORT32A_OUT(x);
}

/* Any code required to disable SPI flash access */
void DFUCustomFlashDisable()
{
    int x;

    PORT32A_PEEK(x);
    x |= P_GPIO_SS_EN_CTRL;
    PORT32A_OUT(x);
}
