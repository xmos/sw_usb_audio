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
#define AUDIO_CLASS_FALLBACK 0

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */ 
//:audio_defs
/* Number of USB streaming channels */
#define NUM_USB_CHAN_IN   (2)         /* Device to Host */
#define NUM_USB_CHAN_OUT  (2)         /* Host to Device */

/* Enable S/PDIF output */
//#define SPDIF         1

/* Run the CODEC as slave, Xcore as master */
#define CODEC_SLAVE   1

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU           1

/* Enable MIDI */
#define MIDI          0

/* Enable IAP */
#define IAP           1

/* Use EXPANSION interface rather than port32A scheme. Implies 48 pin package rather than 128. */
#define IO_EXPANSION 1

#define SELF_POWERED 1

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
/***** Defines relating to iOS identification*****/
#define ACCESSORY_MODEL_NUMBER      "XR-IOS-USB-AUDIO"
#define ACCESSORY_HARDWARE_VERSION  {1, 1, 0}
#define ACCESSORY_FIRMWARE_VERSION  {1, 0, 0}

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
#define DFU_CUSTOM_FLASH_DEVICE
#endif

/* Example custom flash device */
#ifdef DFU_CUSTOM_FLASH_DEVICE
#define DFU_FLASH_DEVICE \
  { \
    NUMONYX_M25P10, \
    256,                    /* page size */ \
    512,                    /* num pages */ \
    3,                      /* address size */ \
    8,                      /* log2 clock divider */ \
    0x9f,                   /* SPI_RDID */ \
    0,                      /* id dummy bytes */ \
    3,                      /* id size in bytes */ \
    0x202011,               /* device id */ \
    0xD8,                   /* SPI_SE */ \
    0,                      /* full sector erase */ \
    0x06,                   /* SPI_WREN */ \
    0x04,                   /* SPI_WRDI */ \
    PROT_TYPE_SR,           /* SR protection */ \
    {{0x0c,0x0},{0,0}},     /* no values */ \
    0x02,                   /* SPI_PP */ \
    0x0b,                   /* SPI_READFAST */ \
    1,                      /* 1 read dummy byte */ \
    SECTOR_LAYOUT_REGULAR,  /* sane sectors */ \
    {32768,{0,{0}}},        /* regular sector size */ \
    0x05,                   /* SPI_RDSR */ \
    0x01,                   /* no SPI_WRSR */ \
    0x01,                   /* SPI_WIP_BIT_MASK */ \
 }
#endif

#endif
