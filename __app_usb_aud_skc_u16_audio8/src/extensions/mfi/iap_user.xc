
#include <xs1.h>
#include <platform.h>

#ifdef IAP
#include "iap_user.h"
#endif
#include "usb_slice_defines.h"

on tile[0] : out port p_usb_slice = XS1_PORT_4C;
on tile[0] : in port p_acc_det = XS1_PORT_1A;

/* Select Apple connector */
void SelectUSBApple(void)
{
    unsigned tmp = USB_SLICE_P4C_CPR_RST_N;

    tmp |= USB_SLICE_P4C_USB_SEL;     // Lightning connector on XA-SK-USB-BLC, USB A connector on XA-SK-USB-ABC

    p_usb_slice <: tmp;
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
    unsigned tmp = USB_SLICE_P4C_CPR_RST_N;

    tmp &= ~USB_SLICE_P4C_USB_SEL;   // USB B connector on XA-SK-USB-BLC and XA-SK-USB-ABC

    p_usb_slice <: tmp;
}

/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    unsigned tmp = 0;
    p_acc_det :> tmp;

    return tmp; //& P_GPI_DEVDET_MASK;
}
