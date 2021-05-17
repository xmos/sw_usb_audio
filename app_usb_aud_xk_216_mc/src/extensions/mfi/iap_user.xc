
#ifdef IAP
#include "app_usb_aud_xk_216_mc.h"

#include <print.h>
#include <platform.h>
#include <xs1.h>

#include "iap_user.h"
#include "gpio_access.h"

on tile[0] : in port p_acc_det = XS1_PORT_4C;

void p_gpio_out(unsigned);
unsigned p_gpio_peek();

/* Select Apple connector */
void SelectUSBApple(void)
{
#ifndef USB_SEL_A
    unsigned tmp = p_gpio_peek();
    tmp &= (~(P_GPIO_USB_SEL0 | P_GPIO_USB_SEL1));
    p_gpio_out(tmp | P_GPIO_USB_SEL0);
#endif
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
#ifndef USB_SEL_A
    unsigned tmp = p_gpio_peek();
    tmp &= (~(P_GPIO_USB_SEL0 | P_GPIO_USB_SEL1));
    p_gpio_out(tmp | P_GPIO_USB_SEL1 | P_GPIO_USB_SEL0);
#endif
}

/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
#ifdef USB_SEL_A
    return 0;
#else
    unsigned tmp;
    p_acc_det :> tmp;

#if XCORE_200_MC_AUDIO_HW_VERSION == 2
    /* ACC_POWER connected to bit[0] */
    return !(tmp & 1);
#else
    /* ACC_POWER connected to bit[1] */
    return !(tmp & 2);
#endif

#endif
}

#endif
