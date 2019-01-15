/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-200 Microphone Array board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_
#endif

/* Prototype for our custom genclock() task */
void genclock();

#define USER_MAIN_CORES \
            on tile[1] : genclock();

/*
 * Device configuration option defines to override default defines found devicedefines.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Tile defines */
#define AUDIO_IO_TILE      1
#define XUD_TILE           1
#define PDM_TILE           0

/* Enable PDM and PDM->PCM conversion code */
#define NUM_PDM_MICS       8

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - Default is 8 in 2 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (8)         /* Device to Host */
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
#define I2S_CHANS_ADC      (0)
#endif

/* Master clock defines (in Hz) */
#define MCLK_441           (256*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (256*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MIN_FREQ
#if(AUDIO_CLASS == 1)
#define MIN_FREQ           (8000)
#else
#define MIN_FREQ           (11025)
#endif

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (48000)
#endif

/* Maximum frequency in full-speed mode */
#ifndef MAX_FREQ_FS
#define MAX_FREQ_FS        (44100)  /* FS can't handle 8in2out at 48000 */
#endif

//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0008) 
#define PID_AUDIO_1        (0x0009) 
#define PRODUCT_STR_A2     "XMOS Microphone Array UAC2.0"
#define PRODUCT_STR_A1     "XMOS Microphone Array UAC1.0"
//:

#endif
