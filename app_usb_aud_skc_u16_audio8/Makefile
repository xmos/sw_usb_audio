# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xp-skc-u16-audio8.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=2*64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=1 -DADAT_TX_USE_SHARED_BUFF=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_i2c_simple module_usb_device module_locks module_adat_rx module_adat_tx

MODULE_LIBRARIES = xud_u


# Test build configs (Note these make use of the defaults in customdefines.h)
MFI ?= 0

ifeq ($(MFI), 0)

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM8
XCC_FLAGS_2io_tdm8 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8
INCLUDE_ONLY_IN_2io_tdm8 =

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM, xCore I2S slave
XCC_FLAGS_2io_tdm8_slave = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2io_tdm8_slave =

XCC_FLAGS_2xo_tdm8 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=0 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=0
INCLUDE_ONLY_IN_2xo_tdm8 =

XCC_FLAGS_2io_tdm16 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=16 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=16 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16
INCLUDE_ONLY_IN_2io_tdm16 =

XCC_FLAGS_2io_tdm24 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=24 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=24 -DNUM_USB_CHAN_OUT=24 -DNUM_USB_CHAN_IN=24
INCLUDE_ONLY_IN_2io_tdm24 =

XCC_FLAGS_2xo_tdm32 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=0 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2xo_tdm32 =

# Audio Class 2, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2io = $(BUILD_FLAGS) -DSPDIF_TX=0
INCLUDE_ONLY_IN_2io =

# Audio Class 2, Input, Output, No MIDI, No SPDIF, XCore I2S Slave
XCC_FLAGS_2io_slave = $(BUILD_FLAGS) -DSPDIF_TX=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2io_slave =

# Audio Class 2, Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2ioxs =

# Audio Class 2, Input, Output, MIDI, SPDIF Tx
XCC_FLAGS_2ioms = $(BUILD_FLAGS) -DMIDI=1
INCLUDE_ONLY_IN_2ioms =

# Audio Class 2, No Input, Output, No MIDI, SPDIF_Tx
XCC_FLAGS_2xoxs = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_2xoxs =

# Audio Class 2, No Input, Output, No MIDI, No SPDIF Tx
XCC_FLAGS_2xoxx = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2xoxx =

# Audio Class 2, No Input, Output, No MIDI, SPDIF, DSD
XCC_FLAGS_2xoxxd = $(BUILD_FLAGS) -DDSD_CHANS_DAC=2 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_2xoxxd =

# Audio Class 1, Input, Output, no MIDI, no SPDIF Tx
XCC_FLAGS_1ioxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_1ioxx = 

# Audio Class 2, Input, Output, ADAT out
XCC_FLAGS_2io_adatout = $(BUILD_FLAGS) -DSPDIF_TX=0 -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16
INCLUDE_ONLY_IN_2io_adatout = 

# Audio Class 2, Input, Output, No MIDI, SPDIF out, SPDIF in
XCC_FLAGS_2io_spdifout_spdifin = $(BUILD_FLAGS) -DSPDIF_RX=1
INCLUDE_ONLY_IN_2io_spdifout_spdifin = 

# Audio Class 2, Input, Output, No MIDI, ADAT in
XCC_FLAGS_2io_adatin = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=16 -DADAT_RX=1 -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2io_adatin = 

else

# MFi test build configs - iAP support enabled

#Audio Class 2, iAP enabled, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx_mfi =

#Audio Class 2, iAP enabled, No Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2xoxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF_TX=0 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_2xoxx_mfi =

#Audio Class 2, iAP enabled, EA Protocol (Native Transport), Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx_mfi_n = $(BUILD_FLAGS) -DIAP=1 -DIAP_EA_NATIVE_TRANS=1 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx_mfi_n =

include mfi.mk

endif




#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common

