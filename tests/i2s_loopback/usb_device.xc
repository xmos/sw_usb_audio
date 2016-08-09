// Copyright (c) 2016, XMOS Ltd, All rights reserved
#include <xs1.h>
#include <xccompat.h>
#include "usb_std_requests.h"
#include "xud.h"
#include "usb_device.h"

unsigned char g_currentConfig = 0;
unsigned char g_interfaceAlt[16];

XUD_Result_t USB_GetSetupPacket(XUD_ep ep_out, XUD_ep ep_in, REFERENCE_PARAM(USB_SetupPacket_t, sp))
{
  return XUD_RES_OKAY;
}

XUD_Result_t USB_StandardRequests(XUD_ep ep_out, XUD_ep ep_in,
    NULLABLE_ARRAY_OF(unsigned char, devDesc_hs), int devDescLength_hs,
    NULLABLE_ARRAY_OF(unsigned char, cfgDesc_hs), int cfgDescLength_hs,
    NULLABLE_ARRAY_OF(unsigned char, devDesc_fs), int devDescLength_fs,
    NULLABLE_ARRAY_OF(unsigned char, cfgDesc_fs), int cfgDescLength_fs,
#ifdef __XC__
    char * unsafe strDescs[],
#else
    char * strDescs[],
#endif
    int strDescsLength, REFERENCE_PARAM(USB_SetupPacket_t, sp), XUD_BusSpeed_t usbBusSpeed)
{
  return XUD_RES_OKAY;
}
