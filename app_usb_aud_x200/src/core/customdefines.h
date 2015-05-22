/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-200 Audio MC Board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

/* Default to hw version 2.0 */
#ifndef XCORE_200_MC_AUDIO_HW_VERSION 
#define XCORE_200_MC_AUDIO_HW_VERSION 2
#endif

#include "user_main.h"

#define AUDIO_IO_TILE   0
#define XUD_TILE        1

#if XCORE_200_MC_AUDIO_HW_VERSION < 2
#define SPDIF_TX_TILE   1
#endif

#define MIDI_TILE       1

#define MIXER 1
#define MAX_MIX_COUNT 0

#define SELF_POWERED 1

/*
 * Device configuration option defines.  Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		0
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF on */
#ifndef SPDIF_TX
#define SPDIF_TX		1
#endif

/* Audio class version to run in - Default is 2.0 */
#ifndef AUDIO_CLASS
#define AUDIO_CLASS (2)
#endif

/* Enable/disable fall back to Audio Class 1.0 when connected to FS hub. */
#ifndef AUDIO_CLASS_FALLBACK
#define AUDIO_CLASS_FALLBACK 0
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - Default is 4 in 4 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN   (10)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT  (10)         /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC     (8)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC     (8)
#endif

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU             1

/* Master clock defines (in Hz) */
#define MCLK_441          (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48           (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ                    (192000)
#endif

/* Index of SPDIF TX channel (duplicated DAC channels 1/2) */
#define SPDIF_TX_INDEX              (0)

/* Default frequency device reports as running at */
/* Audio Class 1.0 friendly freq */
#define DEFAULT_FREQ                (48000)
//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID   (0x20B1) /* XMOS VID */
#define PID_AUDIO_2 (0x0008) /* SKC_SU1 USB Audio Reference Design PID */
#define PID_AUDIO_1 (0x0009) /* SKC_SU1 Audio Reference Design PID */
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       1
#endif

/* Specify FLASH type on U16 sliceKIT */
#define DFU_FLASH_DEVICE FL_DEVICE_NUMONYX_M25P16

#endif
