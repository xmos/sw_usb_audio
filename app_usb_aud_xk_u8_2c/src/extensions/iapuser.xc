#include "gpio_defines.h"
#include "gpio_access.h"

/* Enable/Power-on/Reset etc coProcessor - called before authentication */
void CoProcessorEnable(void)
{
    // RST line pulled up on board. Warm reset not currently supported
}

/* Disable co-processor - Called at end of authentication */
void CoProcessorDisable(void)
{
    // RST line pulled up on board. Warm reset not currently supported
}

/* Select Apple connector */
void SelectUSBDock(void)
{
    unsigned tmp;
    port32A_peek(tmp);
    
    tmp |= P_GPIO_USB_SEL1;     // Lightning connector on XA-SK-USB-BLC, USB A connector on XA-SK-USB-ABC
    tmp &= ~P_GPIO_VBUS_OUT_EN; // Enable 5V charge output to Apple device (5V active low)

    /* Output to port */  
    port32A_out(tmp);
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
    unsigned tmp;
    port32A_peek(tmp);
    
    tmp &= ~P_GPIO_USB_SEL1;   // USB B connector on XA-SK-USB-BLC and XA-SK-USB-ABC
    tmp |= P_GPIO_VBUS_OUT_EN; // Disable 5V charge output to Apple device (5V active low)

    /* Output to port */  
    port32A_out(tmp);
}

extern in port p_sw;
#include <xs1.h>
/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    unsigned tmp = 0;
    p_sw :> tmp;
    
    return tmp & P_GPI_DEVDET_MASK;
}
