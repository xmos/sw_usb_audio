# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xr-usb-audio-2.0
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -DXUD_SERIES_SUPPORT=2

#Test build configs (Note these make use of the defaults in customdefines.h)

# Audio Class 2, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx = $(BUILD_FLAGS) -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx = 

# Audio Class 2, Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS) 
INCLUDE_ONLY_IN_2ioxs = 

# Audio Class 2, No Input, Output, No MIDI, SPDIF
XCC_FLAGS_2xoxs = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 
INCLUDE_ONLY_IN_2ioxs = 

#Audio Class 2, Input, Output, MIDI, No SPDIF
XCC_FLAGS_2iomx = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2iomx = 

# Audio Class 1, Input, Output, No MIDI, SPDIF
XCC_FLAGS_1ioxs = $(BUILD_FLAGS) -DAUDIO_CLASS=1
INCLUDE_ONLY_IN_1ioxs = 

# Audio Class 1, No Input, Output, No MIDI, SPDIF
XCC_FLAGS_1xoxs = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_1xoxs = 

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_usb_device

MODULE_LIBRARIES = xud_l


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
