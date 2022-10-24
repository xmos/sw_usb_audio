/**
 * @file       xua_conf.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE.ai Audio MC Board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _XUA_CONF_H_
#define _XUA_CONF_H_

/*
 * Device configuration option defines to override default defines found lib_xua/api/xua_conf_defaults.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile */

/*** Defines relating to basic functionality ***/
/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI               (0)
#endif

/* Enable/Disable S/PDIF output - Default is S/PDIF off */
#ifndef XUA_SPDIF_TX_EN
#define XUA_SPDIF_TX_EN	   (0)
#endif

/* Enable/Disable S/PDIF input - Default is S/PDIF off */
#ifndef XUA_SPDIF_RX_EN
#define XUA_SPDIF_RX_EN    (0)
#endif

/* Enable/Disable ADAT output - Default is ADAT off */
#ifndef XUA_ADAT_TX_EN
#define XUA_ADAT_TX_EN     (0)
#endif

/* Enable/Disable ADAT input - Default is ADAT off */
#ifndef XUA_ADAT_RX_EN
#define XUA_ADAT_RX_EN     (0)
#endif

/* Enable/Disable Mixing core(s) - Default is on */
#ifndef MIXER
#define MIXER              (1)
#endif

/* Set the number of mixes to perform - Default is 0 i.e mixing disabled */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      (0)
#endif

/* Audio Class version - Default is 2.0 */
#ifndef AUDIO_CLASS
#define AUDIO_CLASS        (2)
#endif

/*** Defines relating to channel counts ***/
/* Number of I2S channels to DACs*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (8)
#endif

/* Number of I2S channels from ADCs */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (8)
#endif

/* Number of USB streaming channels - by default calculate by counting audio interfaces */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (I2S_CHANS_ADC + 2*XUA_SPDIF_RX_EN + 8*XUA_ADAT_RX_EN)  /* Device to Host */
#endif

#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (I2S_CHANS_DAC + 2*XUA_SPDIF_TX_EN + 8*XUA_ADAT_TX_EN)  /* Host to Device */
#endif

/*** Defines relating to channel arrangement/indices ***/
/* Channel index of S/PDIF Tx channels: separate channels after analogue channels (if they fit) */
#ifndef SPDIF_TX_INDEX
    #if (I2S_CHANS_DAC + 2*XUA_SPDIF_TX_EN) <= NUM_USB_CHAN_OUT
        #define SPDIF_TX_INDEX   (I2S_CHANS_DAC)
    #else
        #define SPDIF_TX_INDEX   (0)
    #endif
#endif

/* Channel index of S/PDIF Rx channels: separate channels after analogue channels */
#ifndef SPDIF_RX_INDEX
#define SPDIF_RX_INDEX     (I2S_CHANS_ADC)
#endif

/* Channel index of ADAT Tx channels: separate channels after S/PDIF channels (if they fit) */
#ifndef ADAT_TX_INDEX
    #if (I2S_CHANS_DAC + 2*XUA_SPDIF_TX_EN + 8*XUA_ADAT_TX_EN) <= NUM_USB_CHAN_OUT
        #define ADAT_TX_INDEX    (I2S_CHANS_DAC + 2*XUA_SPDIF_TX_EN)
    #else
        #define ADAT_TX_INDEX    (0)
    #endif
#endif

/* Channel index of ADAT Rx channels: separate channels after S/PDIF channels */
#ifndef ADAT_RX_INDEX
#define ADAT_RX_INDEX      (I2S_CHANS_ADC + 2*XUA_SPDIF_RX_EN)
#endif

/*** Defines relating to audio frequencies ***/
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

/*** Defines relating to feature placement regarding tiles ***/
#define XUD_TILE           (0)
#define PLL_REF_TILE       (0)

#define AUDIO_IO_TILE      (1)
#define MIDI_TILE          (1)

/*** Defines relating to USB descriptor strings and ID's ***/
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0016)
#define PID_AUDIO_1        (0x0017)
#define PRODUCT_STR_A2     "XMOS xCORE.ai MC (UAC2.0)"
#define PRODUCT_STR_A1     "XMOS xCORE.ai MC (UAC1.0)"

/* Version number reported to host - Default matches XMOS release version */
#ifndef BCD_DEVICE_J
#define BCD_DEVICE_J       (7)
#endif
#ifndef BCD_DEVICE_M
#define BCD_DEVICE_M       (0)
#endif
#ifndef BCD_DEVICE_N
#define BCD_DEVICE_N       (0)
#endif

/* Board power source - Default is bus-powered */
#ifndef XUA_POWERMODE
#define XUA_POWERMODE      XUA_POWERMODE_BUS
#endif

/* Enable/Disable example HID code - Default is off */
#ifndef HID_CONTROLS
#define HID_CONTROLS       (0)
#endif

#include "user_main.h"

#endif
