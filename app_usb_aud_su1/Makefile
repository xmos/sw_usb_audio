# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = S1_AUDIO

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DAUDIO_2 -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -DUSB_CORE=0 -DARCH_L -DARCH_S -DBOARD_S1 -D TEST_MODE_SUPPORT 
#-fschedule

XCC_FLAGS_spdif = $(BUILD_FLAGS)
INCLUDE_FLAGS_ONLY_IN_spdif = src/config_spdif

#XCC_FLAGS_midi = $(BUILD_FLAGS)
#INCLUDE_FLAGS_ONLY_IN_midi = src/config_midi

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.

USED_MODULES = module_usb_aud_l1 module_usb_shared module_xud module_usb_aud_shared module_spdif_tx module_spdif_rx module_usb_midi module_dfu

MODULE_LIBRARIES = xud_s


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
