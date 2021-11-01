/**
 * @file       xua_conf.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE.ai eXplorer
 */
#ifndef _XUA_CONF_H_
#define _XUA_CONF_H_

/*
 * Device configuration option defines to override default defines found devicedefines.h
 *
 * Build can be customised but changing and adding defines here
 *
 * Note, we check if they are already defined in Makefile
 */

/* Tile defines */
#define AUDIO_IO_TILE      (1)
#define XUD_TILE           (0)

/* Mixer core enabled by default */
#ifndef MIXER
#define MIXER              (1)
#endif

/* Mixing disabled by default */
#ifndef MAX_MIX_COUNT
#define MAX_MIX_COUNT      (2)
#endif

/* Board is self-powered i.e. not USB bus-powered */
#define SELF_POWERED       (0)

/* Enable/Disable MIDI - Default is MIDI off */
#ifndef MIDI
#define MIDI 		       (0)
#endif

/* Enable/Disable SPDIF output - Default is S/PDIF on */
#ifndef SPDIF_TX
#define SPDIF_TX	       (0)
#endif

/* Defines relating to channel count and channel arrangement (Set to 0 for disable) */
//:audio_defs
/* Number of USB streaming channels - Default is 4 in 4 out */
#ifndef NUM_USB_CHAN_IN
#define NUM_USB_CHAN_IN    (2)          /* Device to Host */
#endif
#ifndef NUM_USB_CHAN_OUT
#define NUM_USB_CHAN_OUT   (2)          /* Host to Device */
#endif

/* Number of IS2 chans to DAC..*/
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
#define PID_AUDIO_2        (0x0008)
#define PID_AUDIO_1        (0x0009)
//:

/* Enable/Disable example HID code */
#ifndef HID_CONTROLS
#define HID_CONTROLS       (0)
#endif


/* Flash part for xcore-AI explorer board: MX25R3235FM1IH0 32MBIT */
#define FL_QUADDEVICE_MX25R3235 \
{ \
    0,                      /* UNKNOWN */ \
    256,                    /* page size */ \
    16384,                  /* num pages */ \
    3,                      /* address size */ \
    3,                      /* log2 clock divider */ \
    0x9F,                   /* QSPI_RDID */ \
    0,                      /* id dummy bytes */ \
    3,                      /* id size in bytes */ \
    0xC22816,               /* device id */ \
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
#define DFU_FLASH_DEVICE FL_QUADDEVICE_MX25R3235

#ifdef __XC__
void AudioHwRemote(chanend c);

extern unsafe chanend uc_audiohw;

#define USER_MAIN_DECLARATIONS chan c_i2s; chan c_audiohw;

#define USER_MAIN_CORES on tile[1]: {\
                                        par\
                                        {\
                                            unsafe{\
                                                uc_audiohw = (chanend) c_audiohw;\
                                            }\
                                        }\
                                    }\
\
                        on tile[0]: {\
                                        par\
                                        {\
                                            AudioHwRemote(c_audiohw);\
                                        }\
                                    } 
#endif
#endif
