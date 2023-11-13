/**
 * @file       xua_conf.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE.ai eXplorer
 */
#ifndef _XUA_CONF_H_
#define _XUA_CONF_H_

#include "../../../shared/version.h"

/*
 * Device configuration option defines to override default defines found in lib_xua/api/xua_conf_default.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Port defines - items missing from XN file */
#define PORT_I2S_DAC0      PORT_I2S_DAC_DATA /* Name conversion from XN file */
#define PORT_I2S_ADC0      PORT_I2S_ADC_DATA /* Name conversion From XN file */
#define PORT_MCLK_IN_USB   XS1_PORT_1D
#define PORT_MCLK_COUNT    XS1_PORT_16B

/* Tile defines */
#define AUDIO_IO_TILE      (1)
#define XUD_TILE           (0)

/* Mixer core disabled by default */
#ifndef MIXER
#define MIXER              (0)
#endif

/* Mixing disabled by default */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      (0)
#endif

/* Board is self-powered i.e. not USB bus-powered */
#define SELF_POWERED       (0)

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       (0)
#endif

/* Enable/Disable S/PDIF output - Default is S/PDIF off */
#ifndef XUA_SPDIF_TX_EN
#define XUA_SPDIF_TX_EN    (0)
#endif

/* Enable/Disable S/PDIF input - Default is S/PDIF off */
#ifndef XUA_SPDIF_RX_EN
#define XUA_SPDIF_RX_EN    (0)
#endif

/* Enable/Disable ADAT output - Default is ADAT off */
#ifndef XUA_ADAT_TX_EN
#define XUA_ADAT_TX_EN     (0)
#endif

/* Enable/Disable ADAT input - Default is ADAT off */
#ifndef XUA_ADAT_RX_EN
#define XUA_ADAT_RX_EN     (0)
#endif

/* Number of I2S chans to DAC */
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (2)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (2)
#endif

/* Master clock defines (in Hz) */
#define MCLK_441           (512*44100)   /* 44.1, 88.2 etc */
#define MCLK_48            (512*48000)   /* 48, 96 etc */

/* Maximum frequency device runs at */
#ifndef MAX_FREQ
#define MAX_FREQ           (192000)
#endif

//:
/***** Defines relating to USB descriptors etc *****/
//:usb_defs
#define VENDOR_ID          (0x20B1) /* XMOS VID */
#define PID_AUDIO_2        (0x0018)
#define PID_AUDIO_1        (0x0019)
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       (0)
#endif

#define FL_QUADDEVICE_AT25FF321A \
{ \
    0,                      /* UNKNOWN */ \
    256,                    /* page size */ \
    16384,                  /* num pages */ \
    3,                      /* address size */ \
    3,                      /* log2 clock divider */ \
    0x9F,                   /* QSPI_RDID */ \
    0,                      /* id dummy bytes */ \
    3,                      /* id size in bytes */ \
    0x1F4708,               /* device id */ \
    0x20,                   /* QSPI_SE */ \
    4096,                   /* Sector erase is always 4KB */ \
    0x06,                   /* QSPI_WREN */ \
    0x04,                   /* QSPI_WRDI */ \
    PROT_TYPE_SR,           /* Protection via SR */ \
    {{0x3C,0x00},{0,0}},    /* QSPI_SP, QSPI_SU */ \
    0x02,                   /* QSPI_PP */ \
    0xEB,                   /* QSPI_READ_FAST */ \
    1,                      /* 1 read dummy byte */ \
    SECTOR_LAYOUT_REGULAR,  /* mad sectors */ \
    {4096,{0,{0}}},         /* regular sector sizes */ \
    0x05,                   /* QSPI_RDSR */ \
    0x01,                   /* QSPI_WRSR */ \
    0x01,                   /* QSPI_WIP_BIT_MASK */ \
}

// DFU_FLASH_DEVICE is a comma-separated list of flash spec structures
// This define is used in sc_usb_audio/module_usb_audio/flashlib_user.c
#define DFU_FLASH_DEVICE FL_QUADDEVICE_AT25FF321A

/* Calculate channel counts based on features */
#if (XUA_SPDIF_TX_EN)
#define SPDIF_TX_CHANS     (2)
#else
#define SPDIF_TX_CHANS     (0)
#endif

#if (XUA_SPDIF_RX_EN)
#define SPDIF_RX_CHANS     (2)
#else
#define SPDIF_RX_CHANS     (0)
#endif

#if (XUA_ADAT_TX_EN)
#define ADAT_TX_CHANS      (8)
#else
#define ADAT_TX_CHANS      (0)
#endif

#if (XUA_ADAT_RX_EN)
#define ADAT_RX_CHANS      (8)
#else
#define ADAT_RX_CHANS      (0)
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - by default calculate by counting audio interfaces */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (I2S_CHANS_ADC + SPDIF_RX_CHANS + ADAT_RX_CHANS)         /* Device to Host */
#endif

#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (I2S_CHANS_DAC + SPDIF_TX_CHANS + ADAT_TX_CHANS)         /* Host to Device */
#endif

/* Channel index of SPDIF Rx channels (duplicated DAC channels 1/2 when index is 0) */
/* If we have enough channels then tag on the end as separate channels, otherwise
 * duplicate channels 1/2 */
#if (NUM_USB_CHAN_OUT >= (I2S_CHANS_DAC+2))
#define SPDIF_TX_INDEX     (I2S_CHANS_DAC)
#else
#define SPDIF_TX_INDEX     (0)
#endif

/* Channel index of SPDIF Rx channels */
#if (NUM_USB_CHAN_IN >= (I2S_CHANS_ADC+2))
#define SPDIF_RX_INDEX     (I2S_CHANS_ADC)
#else
#define SPDIF_RX_INDEX     (0)
#endif

/* Channel index of ADAT Tx channels */
#if (XUA_SPDIF_TX_EN == 1)
#define ADAT_TX_INDEX      (SPDIF_TX_INDEX + 2)
#else
#define ADAT_TX_INDEX      (I2S_CHANS_DAC)
#endif

/* Channel index of ADAT Rx channels */
#if defined(XUA_SPDIF_RX_EN) && (XUA_SPDIF_RX_EN == 1)
#define ADAT_RX_INDEX      (SPDIF_RX_INDEX + 2)
#else
#define ADAT_RX_INDEX      (I2S_CHANS_ADC)
#endif

#endif
