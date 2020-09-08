/**
 * @file       customdefines.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-200 Audio MC Board
 * @author     Ross Owen, XMOS Limited
 */
#ifndef _CUSTOMDEFINES_H_
#define _CUSTOMDEFINES_H_

#include "user_main.h"

/*
 * Device configuration option defines to override default defines found devicedefines.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */



/* Default to board version version 2.0 */
#ifndef XCORE_200_MC_AUDIO_HW_VERSION
#define XCORE_200_MC_AUDIO_HW_VERSION 2
#endif

/* Tile defines */
#define AUDIO_IO_TILE      0
#define XUD_TILE           1

/* SPDIF Tx i/o moved tile between board versions 1.0 -> 2.0 */
#if XCORE_200_MC_AUDIO_HW_VERSION < 2
#define SPDIF_TX_TILE      1
#endif

#define MIDI_TILE          1

/* Mixer core enabled by default */
#ifndef MIXER
#define MIXER              1
#endif

/* Mixing disabled by default */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      0
#endif

/* Board is self-powered i.e. not USB bus-powered */
#define SELF_POWERED       1

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       0
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF on */
#ifndef SPDIF_TX
#define SPDIF_TX	       1
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - Default is 4 in 4 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (10)         /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (10)         /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
#ifndef I2S_CHANS_DAC
#define I2S_CHANS_DAC      (8)
#endif

/* Number of I2S chans from ADC */
#ifndef I2S_CHANS_ADC
#define I2S_CHANS_ADC      (8)
#endif

/* Channel index of SPDIF Rx channels (duplicated DAC channels 1/2 when index is 0) */
#ifndef SPDIF_TX_INDEX
#define SPDIF_TX_INDEX     (8)
#endif

/* Channel index of SPDIF Rx channels */
#ifndef SPDIF_RX_INDEX
#define SPDIF_RX_INDEX     (8)
#endif

/* Channel index of ADAT Tx channels */
#if defined(SPDIF_TX) && (SPDIF_TX==1)
#define ADAT_TX_INDEX      (SPDIF_TX_INDEX + 2)
#else
#define ADAT_TX_INDEX      (I2S_CHANS_DAC)
#endif

/* Channel index of ADAT Rx channels */
#if defined(SPDIF_RX) && (SPDIF_RX==1)
#define ADAT_RX_INDEX      (SPDIF_RX_INDEX + 2)
#else
#define ADAT_RX_INDEX      (I2S_CHANS_ADC)
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
#define PID_AUDIO_2        (0x0008) /* SKC_SU1 USB Audio Reference Design PID */
#define PID_AUDIO_1        (0x0009) /* SKC_SU1 Audio Reference Design PID */
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       1
#endif

#define FL_QUADDEVICE_ISSI_IS25LQ016D \
{ \
    22,                     /* Enum value to identify the flashspec in a list */ \
    256,                    /* page size */ \
    8192,                   /* num pages */ \
    3,                      /* address size */                                   \
    3,                      /* log2 clock divider */                             \
    0x9F,                   /* QSPI_RDID */ \
    0,                      /* id dummy bytes */ \
    3,                      /* id size in bytes */ \
    0x9D6015,               /* device id */ \
    0x20,                   /* QSPI_SE */ \
    4096,                   /* Sector erase is always 4KB */ \
    0x06,                   /* QSPI_WREN */ \
    0x04,                   /* QSPI_WRDI */ \
    PROT_TYPE_NONE,         /* no protection */ \
    {{0,0},{0x00,0x00}},    /* QSPI_SP, QSPI_SU */ \
    0x02,                   /* QSPI_PP */ \
    0xEB,                   /* QSPI_READ_FAST */ \
    1,                      /* 1 read dummy byte */ \
    SECTOR_LAYOUT_REGULAR,  /* mad sectors */ \
    {4096,{0,{0}}},        /* regular sector sizes */ \
    0x05,                   /* QSPI_RDSR */ \
    0x01,                   /* QSPI_WRSR */ \
    0x01,                   /* QSPI_WIP_BIT_MASK */ \
}

// DFU_FLASH_DEVICE is a comma-separated list of flash spec structures
// FL_QUADDEVICE_ISSI_IS25LQ016B: Deprecated integrated flash part
// FL_QUADDEVICE_ISSI_IS25LQ080D: New integrated flash part
// FL_QUADDEVICE_ISSI_IS25LQ080B: External flash part used for this board
// This define is used in sc_usb_audio/module_usb_audio/flashlib_user.c
#define DFU_FLASH_DEVICE \
    FL_QUADDEVICE_ISSI_IS25LQ016B, \
    FL_QUADDEVICE_ISSI_IS25LQ016D, \
    FL_QUADDEVICE_ISSI_IS25LQ080B

#endif
