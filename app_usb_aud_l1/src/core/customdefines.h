/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For L1 USB Audio Reference Design
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

#define XMOS_USB_AUD_APP_MAJOR_VERSION 6
#define XMOS_USB_AUD_APP_MINOR_VERSION 3
#define XMOS_USB_AUD_APP_POINT_VERSION 0

/*
 * Device configuration option defines.  Build can be customised buy changing and adding defines here
 *
 * Note, we chec if they are already defined in Makefile
 */

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI               (0)
#endif

/* Enable/Disable SPDIF - Default is SPDIF off */
#ifndef SPDIF
#define SPDIF              (0)
#endif

/* Audio Class Version.  Note we run in FS when in Audio Class 1.0 mode. Default is 2 */
//:Functionality
#ifndef AUDIO_CLASS
#define AUDIO_CLASS        (2)
#endif

/* Enable Fall-back to audio class 1.0 when connected to FS hub */
#ifndef AUDIO_CLASS_FALLBACK
#define AUDIO_CLASS_FALLBACK (1)
#endif
//:

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
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

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU                (1)

/* Master clock defines (in Hz) */
#define MCLK_441           (256*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

/* Index of SPDIF TX channel (duplicated DAC channels 1/2) */
#define SPDIF_TX_INDEX     (0)

/* Default frequency device reports as running at */
/* Audio Class 1.0 friendly freq */
#define DEFAULT_FREQ       (48000)
//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0002) /* L1 USB Audio Reference Design PID */
#define PID_AUDIO_1        (0x0003) /* L1 USB Audio Reference Design PID */
//:

/* Enables HID EP */
#define HID_CONTROLS       (1)

/* Define to Enable use of custom flash device for DFU interface */
#if defined(DFU_CUSTOM_FLASH_DEVICE) && (DFU_CUSTOM_FLASH_DEVICE==0)
#undef DFU_CUSTOM_FLASH_DEVICE
#else
// Disabled by default
//#define DFU_CUSTOM_FLASH_DEVICE
#endif

/* Example custom flash device */
#ifdef DFU_CUSTOM_FLASH_DEVICE
#define DFU_FLASH_DEVICE \
  { \
    ATMEL_AT25FS010, \
    256,                    /* page size */ \
    512,                    /* num pages */ \
    3,                      /* address size */ \
    8,                      /* log2 clock divider */ \
    0x9F,                   /* SPI_RDID */ \
    0,                      /* id dummy bytes */ \
    3,                      /* id size in bytes */ \
    0x1f6601,               /* device id */ \
    0xD8,                   /* SPI_SE */ \
    0,                      /* erase is full sector */ \
    0x06,                   /* SPI_WREN */ \
    0x04,                   /* SPI_WRDI */ \
    PROT_TYPE_SR,           /* no protection */ \
    {{0x0c,0x02},{0,0}},    /* SR values for protection */ \
    0x02,                   /* SPI_PP */ \
    0x0B,                   /* SPI_READ_FAST */ \
    1,                      /* 1 read dummy byte*/ \
    SECTOR_LAYOUT_REGULAR,  /* sane sectors */ \
    {32768,{0,{0}}},        /* regular sector sizes */ \
    0x05,                   /* SPI_RDSR */ \
    0x01,                   /* SPI_WRSR */ \
    0x01,                   /* SPI_WIP_BIT_MASK */ \
  }
#endif

#endif
