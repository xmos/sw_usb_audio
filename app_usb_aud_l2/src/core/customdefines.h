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
#define AUDIO_CLASS        (2)

/* When connected to a full-speed hub, run in USB Audio Class 2.0 mode */
#define FULL_SPEED_AUDIO_2 (1)

/* Defines relating to channel count and channel arrangement (0 for disable) */
/* Number of USB streaming channels */
#define NUM_USB_CHAN_IN    (10)              /* Device to Host */
#define NUM_USB_CHAN_OUT   (10)              /* Host to Device */

/* S/PDIF Tx enabled by default */
#ifndef SPDIF
#define SPDIF	           1
#endif

/* Enable Mixer Core(s) */
#ifndef MIXER
#define MIXER              1
#endif

/* Disable mixing - mixer core used for volume only */
#define MAX_MIX_COUNT      0

/* Device is self powered (not USB bus powered */
#define SELF_POWERED       1

/* Number of IS2 chans to DAC..*/
#define I2S_CHANS_DAC      (8)

/* Number of I2S chans from ADC */
#define I2S_CHANS_ADC      (6)

/* SPDIF and ADAT first input chan indices */
#define SPDIF_RX_INDEX     (6)
#define ADAT_RX_INDEX      (8)
#define SPDIF_TX_INDEX     (8)

/* Master clock defines (in Hz) */
#define MCLK_441           (512*44100)       /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)       /* 48, 96 etc */

/* Maximum frequency device runs at */
#define MAX_FREQ           (192000)

/***** Defines relating to USB descriptors etc *****/
#define VENDOR_ID          (0x20B1)          /* XMOS VID */
#define PID_AUDIO_1        (0x0005)
#define PID_AUDIO_2        (0x0004)

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
