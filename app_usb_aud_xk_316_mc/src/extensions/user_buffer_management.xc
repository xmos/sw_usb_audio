// Copyright 2017-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xs1.h>
#include <platform.h>
#include <string.h>

#include "xua.h"
#include "xud_device.h"

#ifndef USB_LOOPBACK
#define USB_LOOPBACK (0)
#endif

#if USB_LOOPBACK
#define _MIN_USB_CHANS XUA_MIN(NUM_USB_CHAN_OUT, NUM_USB_CHAN_IN)
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[])
{
    for(int i = 0; i < _MIN_USB_CHANS; i++)
    {
        sampsFromAudioToUsb[i] = sampsFromUsbToAudio[i];
    }
    for(int i=_MIN_USB_CHANS; i<NUM_USB_CHAN_IN; i++)
    {
        sampsFromAudioToUsb[i] = 0;
    }
}
#endif
