// Copyright (c) 2016, XMOS Ltd, All rights reserved
#ifndef __custom_defines_h__
#define __custom_defines_h__

#define EXCLUDE_USB_AUDIO_MAIN
#define NUM_PDM_MICS 0
#define XUD_TILE 1
#define AUDIO_IO_TILE 0
#define MIXER 0
#define MCLK_441 (512 * 44100)
#define MCLK_48 (512 * 48000)
#define MIN_FREQ 44100
#define MAX_FREQ 192000
#define SPDIF_TX_INDEX 0
#define VENDOR_STR "XMOS"
#define VENDOR_ID 0x20B1
#define PRODUCT_STR_A2 "Test device"
#define PRODUCT_STR_A1 "Test device"
#define PID_AUDIO_1 1
#define PID_AUDIO_2 2
#define AUDIO_CLASS 2
#define AUDIO_CLASS_FALLBACK 0
#define BCD_DEVICE 0x1234

#endif // __custom_defines_h__
