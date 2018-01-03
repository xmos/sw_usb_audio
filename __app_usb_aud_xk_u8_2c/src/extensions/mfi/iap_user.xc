#ifdef IAP
#include "iap_user.h"
#endif
#include "gpio_defines.h"
#include "gpio_access.h"

/* Select Apple connector */
void SelectUSBApple(void)
{
    unsigned tmp;
#ifndef USB_SEL_A
    port32A_lock_peek(tmp);

    tmp |= P_GPIO_USB_SEL1;     // Lightning connector on XA-SK-USB-BLC, USB A connector on XA-SK-USB-ABC

    /* Output to port */
    port32A_out_unlock(tmp);
#endif
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
    unsigned tmp;
#ifndef USB_SEL_A
    port32A_lock_peek(tmp);

    tmp &= ~P_GPIO_USB_SEL1;    // USB B connector on XA-SK-USB-BLC and XA-SK-USB-ABC

    /* Output to port */
    port32A_out_unlock(tmp);
#endif
}

extern in port p_sw;
#include <xs1.h>
/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    unsigned tmp = 0;

#ifdef USB_SEL_A
    return 0;
#else
    p_sw :> tmp;
    return !(tmp & P_GPI_DEVDET_MASK);
#endif

}
