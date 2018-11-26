#include <xs1.h>
#include <platform.h>
#include "usb_slice_defines.h"

on tile[0] : out port p_usb_slice = PORT_USB_GPIO;
on tile[0] : in port p_acc_det = PORT_ACC_PWR;

#ifdef IAP
#include "iap_user.h"

/* Only declare this port for MFi builds to avoid conflict with slicekit_slicecard_init.S */
on tile[0] : out port p_vbus_out_en = PORT_VBUS_OUT_EN;

/* Select Apple connector */
void SelectUSBApple(void)
{
    unsigned tmp = USB_SLICE_P4C_CPR_RST_N;

    tmp |= USB_SLICE_P4C_USB_SEL; // Lightning connector on XA-SK-USB-BLC, USB A connector on XA-SK-USB-ABC

    p_usb_slice <: tmp;
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
    unsigned tmp = USB_SLICE_P4C_CPR_RST_N;

    tmp &= ~USB_SLICE_P4C_USB_SEL; // USB B connector on XA-SK-USB-BLC and XA-SK-USB-ABC

    p_usb_slice <: tmp;
}

/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    unsigned tmp = 0;
    p_acc_det :> tmp;

    return !tmp;
}

#endif /* IAP */
