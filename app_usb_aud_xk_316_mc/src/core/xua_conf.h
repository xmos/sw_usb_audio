/**
 * @file       xua_conf.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-AI Audio MC Board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _XUA_CONF_H_
#define _XUA_CONF_H_

/*
 * Device configuration option defines to override default defines found lib_xua/api/xua_conf_defaults.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Tile defines */
#define XUD_TILE           (0)
#define PLL_REF_TILE       (0)

#define AUDIO_IO_TILE      (1)
#define MIDI_TILE          (1)

/* Version number */
#ifndef BCD_DEVICE_J
#define BCD_DEVICE_J       (7)
#endif
#ifndef BCD_DEVICE_M
#define BCD_DEVICE_M       (0)
#endif
#ifndef BCD_DEVICE_N
#define BCD_DEVICE_N       (0)
#endif

/* Mixer core enabled by default */
#ifndef MIXER
#define MIXER              (1)
#endif

/* Mixing disabled by default */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      (0)
#endif

/* Board is self-powered i.e. not USB bus-powered */
#ifndef SELF_POWERED
#define SELF_POWERED       (0)
#endif

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       (0)
#endif

/* Enable/Disable S/PDIF output - Default is S/PDIF off */
#ifndef XUA_SPDIF_TX_EN
#define XUA_SPDIF_TX_EN	   (0)
#endif

/* Enable/Disable S/PDIF input - Default is S/PDIF off */
#ifndef XUA_SPDIF_RX_EN
#define XUA_SPDIF_RX_EN	   (0)
#endif

/* Enable/Disable ADAT output - Default is ADAT off */
#ifndef XUA_ADAT_TX_EN
#define XUA_ADAT_TX_EN	   (0)
#endif

/* Enable/Disable ADAT input - Default is ADAT off */
#ifndef XUA_SPDIF_RX_EN
#define XUA_ADAT_RX_EN	   (0)
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (8)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (8)
#endif

/* Master clock defines (in Hz) */
#ifndef MCLK_441
#define MCLK_441           (512*44100)   /* 44.1, 88.2 etc */
#endif

#ifndef MCLK_48
#define MCLK_48            (512*48000)   /* 48, 96 etc */
#endif

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0016)
#define PID_AUDIO_1        (0x0017)
#define PRODUCT_STR_A2     "XMOS xCORE-AI MC (UAC2.0)"
#define PRODUCT_STR_A1     "XMOS xCORE-AI MC (UAC1.0)"
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       (0)
#endif

/* Calculate channel counts based on features */
#if (XUA_SPDIF_TX_EN)
#define SPDIF_TX_CHANS     (2)
#else
#define SPDIF_TX_CHANS     (0)
#endif

#if (XUA_SPDIF_RX_EN)
#define SPDIF_RX_CHANS     (2)
#else
#define SPDIF_RX_CHANS     (0)
#endif

#if (XUA_ADAT_TX_EN)
#define ADAT_TX_CHANS      (8)
#else
#define ADAT_TX_CHANS      (0)
#endif

#if (XUA_ADAT_RX_EN)
#define ADAT_RX_CHANS      (8)
#else
#define ADAT_RX_CHANS      (0)
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - by default calculate by counting audio interfaces */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (I2S_CHANS_ADC + SPDIF_RX_CHANS + ADAT_RX_CHANS)         /* Device to Host */
#endif

#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (I2S_CHANS_DAC + SPDIF_TX_CHANS + ADAT_TX_CHANS)         /* Host to Device */
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
#if defined(XUA_SPDIF_RX_EN) && (XUA_SPDIF_RXEN == 1)
#define ADAT_RX_INDEX      (SPDIF_RX_INDEX + 2)
#else
#define ADAT_RX_INDEX      (I2S_CHANS_ADC)
#endif

#include "user_main.h"

#endif
