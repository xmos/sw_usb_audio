# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xp-skc-u16-audio8.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=2*64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_i2c_simple module_usb_device

MODULE_LIBRARIES = xud_u


# Test build configs (Note these make use of the defaults in customdefines.h)
MFI ?= 0

ifeq ($(MFI), 0)

# Audio Class 2, Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS) 
INCLUDE_ONLY_IN_2ioxs = 

else

# MFi test build configs - iAP support enabled

#Audio Class 2, iAP enabled, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF=0
INCLUDE_ONLY_IN_2ioxx_mfi = 

#Audio Class 2, iAP enabled, No Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2xoxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF=0 -DNUM_USB_CHAN_IN=0
INCLUDE_ONLY_IN_2xoxx_mfi = 

include mfi.mk

endif




#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common

