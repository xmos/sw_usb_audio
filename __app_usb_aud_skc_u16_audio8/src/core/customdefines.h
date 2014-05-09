/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For U16 USB Audio Reference Design
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

/*
 * Device configuration option defines.  Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Tile on which audio IO is located */
#define AUDIO_IO_TILE 1
#define IAP_TILE 0

/* Enable/Disable MIDI - Default is MIDI on */
#ifndef MIDI
#define MIDI 		0
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF on */
#ifndef SPDIF
#define SPDIF		1
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN   (8)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT  (8)         /* Host to Device */
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC     (8)
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC     (8)
#endif

/* Number of DSD chans to DAC..*/
//#define DSD_CHANS_DAC     (2)

#define MIDI_SHIFT_TX      7

/* Master clock defines (in Hz) */
#define MCLK_441          (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48           (512*48000)   /* 48, 96 etc */

/* Enable Mixer Core(s) */
#ifndef MIXER
#define MIXER              1
#endif

/* Disable mixing - mixer core used for volume only */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      0
#endif

/* Device is self-powered (i.e. not USB bus powered) */
#define SELF_POWERED       1

/* Index of SPDIF TX channel (duplicated DAC channels 1/2 when index is 0) */
#define SPDIF_TX_INDEX              (0)

/***** Defines relating to USB descriptors etc *****/
#define PID_AUDIO_2 (0x000C) /* XMOS U16 - Audio Class 2.0 */
#define PID_AUDIO_1 (0x000D) /* XMOS U16 - Audio Class 1.0 */

/* Enable/Disable example HID code */
#define HID_CONTROLS       0

/* Specify FLASH type on U16 sliceKIT */
#define DFU_FLASH_DEVICE FL_DEVICE_NUMONYX_M25P16 

#endif
