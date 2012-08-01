# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = XR-USB-AUDIO-2.0-MC
APP_NAME=usb_audio

# The flags passed to xcc when building the application
BUILD_FLAGS     += -DAUDIO_2 
XCC_FLAGS       = $(BUILD_FLAGS) -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -DIAP -DARCH_L 
#-fschedule


# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.

USED_MODULES = module_usb_aud_l2 module_usb_shared module_xud module_usb_aud_shared module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_usb_audio_adat module_ios


MODULE_LIBRARIES = xud_l

XCC_FLAGS_nomidi = $(XCC_FLAGS)
XCC_FLAGS_midi = $(XCC_FLAGS)


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
