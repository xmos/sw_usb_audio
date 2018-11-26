/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

/*
 * Device configuration option defines.  Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       0
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF on */
#ifndef SPDIF_TX
#define SPDIF_TX		   1
#endif

/* Audio class version to run in - Default is 2.0 */
#ifndef AUDIO_CLASS
#define AUDIO_CLASS        (2)
#endif

/* Enable Audio class 2.0 when connected to a FS hub */
#ifndef FULL_SPEED_AUDIO_2
#define FULL_SPEED_AUDIO_2 1
#endif

/* Enable/disable fall back to Audio Class 1.0 when connected to FS hub. */
#ifndef AUDIO_CLASS_FALLBACK
#define AUDIO_CLASS_FALLBACK 0
#endif


/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN   (2)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT  (2)         /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC     (2)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC     (2)
#endif

/* Enable/Disable IAP - Default is IAP off */
#ifndef IAP
#define IAP                0
#endif

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU                (1)

/* MIDI Tx on bit 7 */
#define MIDI_SHIFT_TX      (7)

/* Master clock defines (in Hz) */
#define MCLK_441           (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

/* Index of SPDIF TX channel (duplicated DAC channels 1/2) */
#define SPDIF_TX_INDEX     (0)

#define SELF_POWERED 1

/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x000A) /* XR-USB-AUDIO-U8-2C PID*/
#define PID_AUDIO_1        (0x000B)
//:

/* Enable/Disable example HID code */
#define HID_CONTROLS       0

/* Enable/Disable SU1 ADC and example code */
#define SU1_ADC_ENABLE     0

/* Define to use custom flash part not in tools by default
 * Device is M25P40 */
#define DFU_FLASH_DEVICE   FL_DEVICE_MICRON_M25P40

#endif
