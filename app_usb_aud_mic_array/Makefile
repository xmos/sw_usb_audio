# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = mic_array_ref.xn
APP_NAME = 

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lquadflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=4 -march=xs2a -DUSB_TILE=tile[1] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_mic_array lib_mic_array_board_support lib_logging module_dfu module_i2c_shared module_i2c_single_port module_usb_audio module_usb_device module_usb_midi module_usb_shared module_xud

# Build config naming scheme:

XCC_FLAGS_demo = $(BUILD_FLAGS) 
INCLUDE_ONLY_IN_demo =

XCC_FLAGS_demo_tdm = $(BUILD_FLAGS) -DI2S_MODE_TDM=1 -DI2S_CHANS_DAC=8
INCLUDE_ONLY_IN_demo_tdm =

MODULE_LIBRARIES = xud_x200

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
