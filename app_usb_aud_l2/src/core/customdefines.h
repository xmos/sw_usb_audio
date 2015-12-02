/**
 * @file        customdefines.h
 * @brief       Defines relating to device configuration and customisation.
 * @author      Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

#include "user_main.h"

/***** Device configuration option defines.  Build can be customised but changing these defines  *****/

/* Audio I/O is on tile 1 */
#define AUDIO_IO_TILE 1

/* Audio Class Version */
#ifndef AUDIO_CLASS
#define AUDIO_CLASS        (2)
#endif

/* When connected to a full-speed hub, run in USB Audio Class 2.0 mode */
#ifndef FULL_SPEED_AUDIO_2
#if (AUDIO_CLASS == 2)
#define FULL_SPEED_AUDIO_2 (1)
#else
#define FULL_SPEED_AUDIO_2 (0)
#endif
#endif

/* Defines relating to channel count and channel arrangement (0 for disable) */
/* Number of USB streaming channels */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (10)              /* Device to Host */
#endif

#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (10)              /* Host to Device */
#endif

/* S/PDIF Tx enabled by default */
#ifndef SPDIF_TX
#define SPDIF_TX           1
#endif

/* Enable Mixer Core(s) */
#ifndef MIXER
#define MIXER              1
#endif

/* Disable mixing - mixer core used for volume only */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      0
#endif

/* Device is self powered (i.e. not USB bus powered) */
#define SELF_POWERED       1

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (8)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (6)
#endif

/* SPDIF and ADAT first input chan indices */
#define SPDIF_RX_INDEX     (6)
#define ADAT_RX_INDEX      (8)
#define SPDIF_TX_INDEX     (I2S_CHANS_DAC)

#if defined(SPDIF_TX) && (SPDIF_TX==1)
#define ADAT_TX_INDEX      (SPDIF_TX_INDEX+2)
#else
#define ADAT_TX_INDEX      (I2S_CHANS_DAC)
#endif

/* Master clock defines (in Hz) */
#define MCLK_441           (512*44100)       /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)       /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

/***** Defines relating to USB descriptors etc *****/
#define VENDOR_ID          (0x20B1)          /* XMOS VID */
#define PID_AUDIO_1        (0x0005)
#define PID_AUDIO_2        (0x0004)

/* Flash device for DFU.  Device supported by tools so no need to spec */
#define DFU_FLASH_DEVICE FL_DEVICE_ATMEL_AT25DF041A

#endif
