# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = mic_array_ref.xn
APP_NAME = 

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lquadflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=4 -march=xs2a -DUSB_TILE=tile[1] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1 -Wno-timing

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_mic_array lib_logging module_dfu module_i2c_shared module_i2c_single_port module_usb_audio module_usb_device module_usb_midi module_usb_shared module_xud

# Build config naming scheme:
#
# Audio Class:  1 or 2
# Input 	enabled: i (channelcount)
# Output 	enabled: o (channelcount)
# e.g. 2i8o8: Audio class 2.0, input and output enabled (8 channels each)

XCC_FLAGS_2i8o2 = $(BUILD_FLAGS) 
INCLUDE_ONLY_IN_2i8o2 =

XCC_FLAGS_1i8o2 = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN_FS=8 -DNUM_USB_CHAN_OUT_FS=2 -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16
INCLUDE_ONLY_IN_1i8o2 = 

MODULE_LIBRARIES = xud_x200

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
