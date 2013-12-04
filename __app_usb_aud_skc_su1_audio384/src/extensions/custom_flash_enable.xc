
extern out port p_gpio;

#include "p_gpio.h"
#include "p_gpio_defines.h"

/* Any code required to enable SPI flash access */
void DFUCustomFlashEnable()
{
    int x;

    x = p_gpio_peek();
    x &= (~P_GPIO_SS_EN_CTRL);
    p_gpio_out(x);
}

/* Any code required to disable SPI flash access */
void DFUCustomFlashDisable()
{
    int x;

    x = p_gpio_peek();
    x |= P_GPIO_SS_EN_CTRL;
    p_gpio_out(x);
}
