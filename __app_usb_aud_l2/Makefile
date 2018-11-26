# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xr-usb-audio-2.0-mc
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     =  -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -DXUD_SERIES_SUPPORT=2 -DXSCOPE=1 -fxscope -DADAT_TX_USE_SHARED_BUFF=1
#-fschedule

TEST_DFU_1 ?= 0
ifeq ($(TEST_DFU_1),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9901
endif
TEST_DFU_2 ?= 0
ifeq ($(TEST_DFU_2),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9902
endif

#Test build configs (Note these make use of the defaults in customdefines.h)

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM
XCC_FLAGS_2io_tdm8 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8
INCLUDE_ONLY_IN_2io_tdm8 =

# Audio Class 2, no Input, Output, no MIDI, SPDIF
XCC_FLAGS_2xoxs = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=1 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_2xoxs = 

# Audio Class 2, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx = $(BUILD_FLAGS) -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx =  

# Audio Class 2, Input, Output, No MIDI, No SPDIF, Mixing
XCC_FLAGS_2ioxx_mix8 = $(BUILD_FLAGS) -DSPDIF_TX=0 -DMAX_MIX_COUNT=8
INCLUDE_ONLY_IN_2ioxx_mix8 =  

# Audio Class 2, Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2ioxs = 

# Audio Class 2, Input, Output, MIDI, no SPDIF
XCC_FLAGS_2iomx = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2iomx = 

# Audio Class 1, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_1ioxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_1ioxx = 

# Audio Class 2, Input, Output, No MIDI, SPDIF out, SPDIF in
XCC_FLAGS_2io_spdifout_spdifin = $(BUILD_FLAGS) -DSPDIF_RX=1
INCLUDE_ONLY_IN_2io_spdifout_spdifin = 

# Audio Class 2, Input, Output, ADAT out
XCC_FLAGS_2io_adatout = $(BUILD_FLAGS) -DSPDIF_TX=0 -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16
INCLUDE_ONLY_IN_2io_adatout = 

# Audio Class 2, Input, Output, SPDIF out, ADAT out
XCC_FLAGS_2io_spdifout_adatout = $(BUILD_FLAGS) -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=18
INCLUDE_ONLY_IN_2io_spdifout_adatout = 

# Audio Class 2, Input, Output, No MIDI, SPDIF out, SPDIF in, Mixer enabled
XCC_FLAGS_2io_spdifout_spdifin_mix8 = $(BUILD_FLAGS) -DSPDIF_RX=1 -DMAX_MIX_COUNT=8 -DLEVEL_METER_LEDS=1 -DLEVEL_METER_HOST=1
INCLUDE_ONLY_IN_2io_spdifout_spdifin_mix8 = 

# Audio Class 2, Input, Output, No MIDI, ADAT in
XCC_FLAGS_2io_adatin = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=16 -DADAT_RX=1 -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2io_adatin = 

# Audio Class 1, no Input, Output, no MIDI, no SPDIF
XCC_FLAGS_1xoxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DMIDI=0 -DSPDIF_TX=0 -DNUM_USB_CHAN_IN=0
INCLUDE_ONLY_IN_1xoxx = 

ifeq ($(TEST_CONFIGS),1)
XCC_FLAGS_2ioxs_codec_master = $(BUILD_FLAGS) -DCODEC_MASTER=1
endif

ifeq ($(TEST_CONFIGS),1)
	XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
	XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2
endif


# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_usb_device module_i2c_simple module_adat_rx module_adat_tx

MODULE_LIBRARIES = xud_l


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
