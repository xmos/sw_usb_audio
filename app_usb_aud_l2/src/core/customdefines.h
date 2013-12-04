/**
 * @file        customdefines.h
 * @brief       Defines relating to device configuration and customisation.
 * @author      Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

#define AUDIO_IO_TILE 1

/***** Device configuration option defines.  Build can be customised but changing these defines  *****/

/* Audio Class Version */
#define AUDIO_CLASS 2
//#define AUDIO_CLASS_FALLBACK 1
#define FULL_SPEED_AUDIO_2 1

/* Defines relating to channel count and channel arrangement (0 for disable) */
/* Number of USB streaming channels */
#define NUM_USB_CHAN_IN             (4)               /* Device to Host */
#define NUM_USB_CHAN_OUT            (4)               /* Host to Device */

/* Define to Enable S/SPDIF output.  Note if OUTPUT is not defined, this just outputs 0 samples */
#if defined(SPDIF) && (SPDIF==0)
#undef SPDIF
#else
// Enabled by default
#define SPDIF	           0
#endif

/* Define to enable S/PDIF Rx.  Note, this also effects glock gen thread and clock unit descriptors */
#if defined(SPDIF_RX) && (SPDIF_RX==0)
#undef SPDIF_RX
#else
// Enabled by default
#define SPDIF_RX           0
#endif

/* Define to enable ADAT Rx.  Note, this also effects glock gen thread and clock unit descriptors */
#if defined(ADAT_RX) && (ADAT_RX==0)
#undef ADAT_RX
#else
// Enabled by default
#define ADAT_RX           0
#endif

#define SELF_POWERED 1

/* Define for CODEC operation mode (i.e. slave/master)*/
#if defined(CODEC_SLAVE) && (CODEC_SLAVE==0)
#undef CODEC_SLAVE
#else
// Enabled by default
#define CODEC_SLAVE        1
#endif

#define DFU 1

/* Define to Enable use of custom flash device for DFU interface */
#if defined(DFU_CUSTOM_FLASH_DEVICE) && (DFU_CUSTOM_FLASH_DEVICE==0)
#undef DFU_CUSTOM_FLASH_DEVICE
#else
// Disabled by default
//#define DFU_CUSTOM_FLASH_DEVICE
#endif

/* Define for enabling MIDI input/output */
//#if defined(MIDI) && (MIDI==0)
//#undef MIDI
//#else
/// Enabled by default
//#define MIDI         1
//#endif

/* Define for enabling mixer interface */
//#if defined(MIXER) && (MIXER==0)
#undef MIXER
//#else
// Enabled by default
//#define MIXER
//#endif

#ifndef MIN_VOLUME
/* The minimum volume setting above -inf. This is a signed 8.8 fixed point
 number that must be strictly greater than -128 (0x8000) */
/* Default min volume is -127.5db */
#define MIN_VOLUME (0x8080)
#endif

#ifndef MAX_VOLUME
/* The maximum volume setting. This is a signed 8.8 fixed point number. */
/* Default min volume is 6db */
#define MAX_VOLUME (0x0000)
#endif

#ifndef VOLUME_RES
/* The resolution of the volume control in db as a 8.8 fixed point number */
/* Default volume resolution 1db */
#define VOLUME_RES (0x080)
#endif


#ifndef MIN_MIXER_VOLUME
/* The minimum volume setting for the mixer unit above -inf.
 This is a signed 8.8 fixed point
 number that must be strictly greater than -128 (0x8000) */
/* Default min volume is -127db */
#define MIN_MIXER_VOLUME (0x8080)
#endif

#ifndef MAX_MIXER_VOLUME
/* The maximum volume setting for the mixer.
 This is a signed 8.8 fixed point number. */
/* Default min volume is 0db */
#define MAX_MIXER_VOLUME (0x0C00)
#endif

#ifndef VOLUME_RES_MIXER
/* The resolution of the volume control in db as a 8.8 fixed point number */
/* Default volume resolution 1db */
#define VOLUME_RES_MIXER (0x080)
#endif



/* Number of IS2 chans to DAC..*/
#define I2S_CHANS_DAC               (0)

/* Number of I2S chans from ADC */
#define I2S_CHANS_ADC               (4)


/* SPDIF and ADAT first input chan indices */
#define SPDIF_RX_INDEX              (6)
#define ADAT_RX_INDEX               (8)
#define SPDIF_TX_INDEX              (8)


/* Master clock defines (in Hz) */
#define MCLK_441                 (512*44100)      /* 44.1, 88.2 etc */
#define MCLK_48                  (512*48000)      /* 48, 96 etc */

/* Maximum frequency device runs at */
#define MAX_FREQ                 (192000)

/* Default frequency device reports as running at */
#define DEFAULT_FREQ             (MAX_FREQ)

/***** Defines relating to USB descriptors etc *****/
#define VENDOR_STR				 "XMOS "
#define VENDOR_ID                (0x20B1)        /* XMOS VID */
#define PID_AUDIO_1              (0x0005)
#define PID_AUDIO_2              (0x0004)
#ifndef BCD_DEVICE
#define BCD_DEVICE               (0x0530)        /* Device release number in BCD: 0xJJMN
* JJ: Major, M: Minor, N: Sub-minor */
#endif

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


//#define  LEVEL_METER_PROCESSING     1
//#define  LEVEL_METER_LEDS           1           /* Enables call to VendorLedRefresh() */
//#define  CLOCK_VALIDITY_CALL        0           /* Enables calls to VendorClockValidity(int valid) */
#define  HOST_ACTIVE_CALL           0           /* Enabled call to VendorHostActive(int active); */

#if 0
#ifdef HOST_ACTIVE_CALL                         /* L2 ref design board uses audio core reqs for host active */
#ifndef VENDOR_AUDCORE_REQS
#define  VENDOR_AUDCORE_REQS        1
#endif

#ifndef iENDOR_AUDIO_REQS
#define  VENDOR_AUDIO_REQS          1
#endif
#endif
#endif

//#define MAX_MIX_OUTPUTS             0


#endif
