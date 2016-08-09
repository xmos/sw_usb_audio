// Copyright (c) 2016, XMOS Ltd, All rights reserved
#ifndef __usb_device_h__
#define __usb_device_h__

#include <xs1.h>
#include <xccompat.h>
#include "usb_std_requests.h"
#include "xud.h"

XUD_Result_t USB_GetSetupPacket(XUD_ep ep_out, XUD_ep ep_in, REFERENCE_PARAM(USB_SetupPacket_t, sp));

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
    int strDescsLength, REFERENCE_PARAM(USB_SetupPacket_t, sp), XUD_BusSpeed_t usbBusSpeed);

#endif // __usb_device_h__
