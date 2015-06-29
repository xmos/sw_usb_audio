/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For L1 USB Audio Reference Design
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

/*
 * Device configuration option defines.  Build can be customised buy changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile */

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI               (0)
#endif

/* Enable/Disable SPDIF - Default is SPDIF on */
#ifndef SPDIF_TX
#define SPDIF_TX           (1)
#endif

/* Audio Class Version.  Note we run in FS when in Audio Class 1.0 mode. Default is 2 */
#ifndef AUDIO_CLASS
#define AUDIO_CLASS        (2)
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
/* Number of USB streaming channels - Default is 2 in 2 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (2)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (2)         /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (2)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (2)
#endif

/* Index of SPDIF TX channel (duplicated DAC channels 1/2) */
#define SPDIF_TX_INDEX     (0)

/* Master clock defines (in Hz) */
#define MCLK_441           (256*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0002) /* L1 USB Audio Reference Design PID */
#define PID_AUDIO_1        (0x0003) /* L1 USB Audio Reference Design PID */
//:

/* Enables HID EP */
#define HID_CONTROLS       (1)

/* SPI Flash spec for DFU */
#define DFU_FLASH_DEVICE   FL_DEVICE_ATMEL_AT25FS010

#endif
