# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = pip.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -Os -report -lquadflash -fsubword-select -save-temps -g -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=4 -march=xs2a -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1 -mno-dual-issue

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_adat_rx module_adat_tx module_dfu module_i2c_simple module_spdif_rx module_spdif_tx module_usb_audio module_usb_device module_usb_midi module_usb_shared module_xud

# Build config naming scheme:

# Audio Class:  1 or 2
# Input 	enabled: i (channelcount)
# Output 	enabled: o (channelcount)
# MIDI 		enabled: m, disabled: x
# SPDIF out	enabled: s, disabled: x
# SPDIF in 	enabled: s, disabled: x
# ADAT out	enabled: a, disabled: x
# ADAT in	enabled: a, disabled: x
# DSD out	enabled: d, disabled: x
# e.g. 2i10o10xsxxx: Audio class 2.0, input and output enabled (10 channels each), SPDIF output, no SPDIF input, no ADAT

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2i10o10xxxxxx_slave = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2i10o10xxxxxx_slave = 

MODULE_LIBRARIES = xud_x200

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
