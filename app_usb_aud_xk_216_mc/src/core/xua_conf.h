/**
 * @file       xua_conf.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-200 Audio MC Board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _XUA_CONF_H_
#define _XUA_CONF_H_

#include "app_usb_aud_xk_216_mc.h"

/*
 * Device configuration option defines to override default defines found devicedefines.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Tile defines */
#define AUDIO_IO_TILE      0
#define XUD_TILE           1

#ifndef BCD_DEVICE_J
#define BCD_DEVICE_J       (8)
#endif
#ifndef BCD_DEVICE_M
#define BCD_DEVICE_M       (0)
#endif
#ifndef BCD_DEVICE_N
#define BCD_DEVICE_N       (0)
#endif

/* SPDIF Tx i/o moved tile between board versions 1.0 -> 2.0 */
#if XCORE_200_MC_AUDIO_HW_VERSION < 2
#define SPDIF_TX_TILE      1
#endif

#define MIDI_TILE          1

#define PLL_REF_TILE       (0)

/* Mixer core enabled by default */
#ifndef MIXER
#define MIXER              1
#endif

/* Mixing disabled by default */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      0
#endif

/* Board is self-powered i.e. not USB bus-powered */
#define XUA_POWERMODE      XUA_POWERMODE_SELF

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       0
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF off */
#ifndef XUA_SPDIF_TX_EN
#define XUA_SPDIF_TX_EN	   (0)
#endif

/* Enable/Disable SPDIF input - Default is S/PDIF off */
#ifndef XUA_SPDIF_RX_EN
#define XUA_SPDIF_RX_EN	   (0)
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - Default is 4 in 4 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (10)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (10)         /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (8)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (8)
#endif

/* Channel index of SPDIF Rx channels (duplicated DAC channels 1/2 when index is 0) */
/* If we have enough channels then tag on the end as separate channels, otherwise
 * duplicate channels 1/2 */
#if (NUM_USB_CHAN_OUT >= (I2S_CHANS_DAC+2))
#define SPDIF_TX_INDEX     (I2S_CHANS_DAC)
#else
#define SPDIF_TX_INDEX     (0)
#endif

/* Channel index of SPDIF Rx channels */
#if (NUM_USB_CHAN_IN >= (I2S_CHANS_ADC+2))
#define SPDIF_RX_INDEX     (I2S_CHANS_ADC)
#else
#define SPDIF_RX_INDEX     (0)
#endif

/* Channel index of ADAT Tx channels */
#if (XUA_SPDIF_TX_EN == 1)
#define ADAT_TX_INDEX      (SPDIF_TX_INDEX + 2)
#else
#define ADAT_TX_INDEX      (I2S_CHANS_DAC)
#endif

/* Channel index of ADAT Rx channels */
#if (XUA_SPDIF_RX_EN == 1)
#define ADAT_RX_INDEX      (SPDIF_RX_INDEX + 2)
#else
#define ADAT_RX_INDEX      (I2S_CHANS_ADC)
#endif

/* Master clock defines (in Hz) */
#define MCLK_441           (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x000E) /* XK-AUDIO-216-MC USB Audio Reference Design PID */
#define PID_AUDIO_1        (0x000F) /* XK-AUDIO-216-MC USB Audio Reference Design PID */
#define PRODUCT_STR_A2     "XMOS xCORE-200 MC (UAC2.0)"
#define PRODUCT_STR_A1     "XMOS xCORE-200 MC (UAC1.0)"
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       (1)
#endif

#include "user_main.h"

#endif
