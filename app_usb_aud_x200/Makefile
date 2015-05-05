# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = x200-mc-audio.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=4 -march=xs2a -DUSB_TILE=tile[1] -DADAT_TX_USE_SHARED_BUFF=1 

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_usb_device module_i2c_shared module_i2c_single_port module_adat_tx

MFI ?= 0

ifeq ($(MFI), 0)

# Test build configs (Note these make use of the defaults in customdefines.h)

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM (8in/8out)
XCC_FLAGS_2io_tdm8 = $(BUILD_FLAGS) -DSPDIF=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=192000 -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8
INCLUDE_ONLY_IN_2io_tdm8 =

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM (8in/8out)
XCC_FLAGS_2io_tdm16 = $(BUILD_FLAGS) -DSPDIF=0 -DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DI2S_CHANS_DAC=16 -DI2S_CHANS_ADC=16 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16
INCLUDE_ONLY_IN_2io_tdm16 =

# Audio Class 2, Input, Output, No MIDI, No SPDIF, TDM (32in/32out)
XCC_FLAGS_2io_tdm32 = $(BUILD_FLAGS) -DSPDIF=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2io_tdm32 =

# Audio Class 2, Input, Output, No MIDI, SPDIF, TDM (32in/32out)
XCC_FLAGS_2io_tdm32_spdifout = $(BUILD_FLAGS) -DSPDIF=1 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2io_tdm32_spdifout =

# Audio Class 2, Input, Output, MIDI, SPDIF
XCC_FLAGS_2ioms = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF=1
INCLUDE_ONLY_IN_2ioms = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF=1
INCLUDE_ONLY_IN_2ioxs = 

# Audio Class 2, Input, Output, No Midi, SPDIF, DSD
XCC_FLAGS_2ioxsd = $(BUILD_FLAGS) -DSPDIF=1 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2ioxsd = 

# Audio Class 2, Input, Output, ADAT out
XCC_FLAGS_2io_adatout = $(BUILD_FLAGS) -DSPDIF=0 -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16
INCLUDE_ONLY_IN_2io_adatout = 

else

# MFi test build configs - iAP support enabled
	
# # Audio Class 2, iAP enabled, No Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs_mfi = $(BUILD_FLAGS) -DIAP=1 -DSPDIF=1 -DMIDI=0
INCLUDE_ONLY_IN_2ioxs_mfi = 

# # Audio Class 2, iAP enabled, No Input, Output, No MIDI, SPDIF, DSD
XCC_FLAGS_2ioxsd_mfi = $(BUILD_FLAGS) -DIAP=1 -DSPDIF=1 -DMIDI=0 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2ioxsd_mfi = 

#Audio Class 2, iAP enabled, EA Protocol (Native Transport), Input, Output, No MIDI, No SPDIF. i
# Hid controls disabled (buttons used for EA)
XCC_FLAGS_2ioxx_mfi_n = $(BUILD_FLAGS) -DIAP=1 -DIAP_EA_NATIVE_TRANS=1 -DMIDI=0 -DSPDIF=0 -DHID_CONTROLS=0
INCLUDE_ONLY_IN_2ioxx_mfi_n =

#Audio Class 2, iAP enabled, Input, Output, No,  No SPDIF. Select USB A port. Ignore VBUS.
#Note, this is the config used for Apple role-switch
XCC_FLAGS_2ioxx_usba_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF=0 -DUSB_SEL_A=1 -DXUD_PWR_CFG=0
INCLUDE_ONLY_IN_2ioxx_usba_mfi = 


include mfi.mk

endif


MODULE_LIBRARIES = xud_x200

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
