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
/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */ 
//:audio_defs
/* Number of USB streaming channels - Default is 4 in 4 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN   (0)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT  (2)         /* Host to Device */
#endif

#ifndef SPDIF 
#define SPDIF 0
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC     (2)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC     (0)
#endif

/* Enable DFU interface, Note, requires a driver for Windows */
#define DFU             1

/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID   (0x20B1) /* XMOS VID */
#define PID_AUDIO_2 (0x0008) /* SKC_SU1 USB Audio Reference Design PID */
#define PID_AUDIO_1 (0x0009) /* SKC_SU1 Audio Reference Design PID */
//:

#define PRODUCT_STR "xCORE USB Audio 2.0 - 384kHz"

/* Define to use custom flash part not in tools by default 
 * Device is M25P40 */
#define DFU_FLASH_DEVICE \
{    \
    1, \
    256,                    /* page size */\
    1024,                   /* num pages */\
    3,                      /* address size */\
    8,                      /* log2 clock divider */\
    0x9f,                   /* SPI_RDID */\
    0,                      /* id dummy bytes */\
    3,                      /* id size in bytes */ \
    0x202013,               /* device id */\
    0xD8,                   /* SPI_SE */\
    0,                      /* full sector erase */\
    0x06,                   /* SPI_WREN */\
    0x04,                   /* SPI_WRDI */\
    PROT_TYPE_SR,           /* SR protection */\
    {{0x0c,0x0},{0,0}},     /* no values */\
    0x02,                   /* SPI_PP */\
    0x0b,                   /* SPI_READFAST */\
    1,                      /* 1 read dummy byte */\
    SECTOR_LAYOUT_REGULAR,  /* sane sectors */\
    {32768,{0,{0}}},        /* regular sector size */\
    0x05,                   /* SPI_RDSR */\
    0x01,                   /* no SPI_WRSR */\
    0x01,                   /* SPI_WIP_BIT_MASK */\
}

#endif
