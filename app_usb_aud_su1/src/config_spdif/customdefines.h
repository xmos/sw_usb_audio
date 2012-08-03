/** 
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For L1 USB Audio Reference Design
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

/***** Device configuration option defines.  Build can be customised but changing these defines  *****/

/* Audio Class Version.  Note we run in FS when in Audio Class 1.0 mode */
//:Functionality
/* Enable Fall-back to audio class 1.0 a FS */
#define AUDIO_CLASS (2)

/* Enable Fall-back to audio class 1.0 when connected to FS hub */
#define AUDIO_CLASS_FALLBACK 1
//:

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */ 
//:audio_defs
/* Number of USB streaming channels */
#define NUM_USB_CHAN_IN   (2)         /* Device to Host */
#define NUM_USB_CHAN_OUT  (2)         /* Host to Device */

/* Enable S/PDIF output */
#define SPDIF           1

/* Run the CODEC as slave, Xcore as master */
#define CODEC_SLAVE     1

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU             1

/* Disable MIDI */
#define MIDI            0

#define MIDI_SHIFT_TX   7

/* Number of IS2 chans to DAC..*/
#define I2S_CHANS_DAC     (2)

/* Number of I2S chans from ADC */
#define I2S_CHANS_ADC     (2)

/* Master clock defines (in Hz) */
#define MCLK_441          (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48           (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#define MAX_FREQ                    (192000)       

/* Index of SPDIF TX channel (duplicated DAC channels 1/2) */
#define SPDIF_TX_INDEX              (0)

/* Default frequency device reports as running at */
/* Audio Class 1.0 friendly freq */       
#define DEFAULT_FREQ                (48000)            
//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID   (0x20B1) /* XMOS VID */
#define PID_AUDIO_2 (0x0002) /* L1 USB Audio Reference Design PID */
#define PID_AUDIO_1 (0x0003) /* L1 USB Audio Reference Design PID */
#define BCD_DEVICE  (0x0600) /* Device release number in BCD: 0xJJMN
                              * JJ: Major, M: Minor, N: Sub-minor */
//:

#define HOST_ACTIVE_CALL 1


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
