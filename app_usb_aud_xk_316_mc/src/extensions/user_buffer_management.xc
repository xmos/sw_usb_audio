// Copyright 2017-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xs1.h>
#include <platform.h>
#include <string.h>

#include "xua.h"
#include "xud_device.h"

#if SAMPLE_LOOPBACK
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[])
{
    for(int i = 0; i < NUM_USB_CHAN_OUT; i++)
    {
        sampsFromAudioToUsb[i] = sampsFromUsbToAudio[i];
    }
}
#endif
