# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-316-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -DFLASH_MAX_UPGRADE_SIZE=64*1024 -save-temps -fcomment-asm -Xmapper --map -Xmapper MAPFILE -O3 -report -lquadflash -g -fxscope -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xua lib_xud lib_spdif lib_i2c lib_adat

# Build config naming scheme:

# Audio Class:  	1 or 2
# Sync Mode 		A(sync) S(ync)
# Input 			enabled: i (channelcount)
# Output 			enabled: o (channelcount)
# MIDI 				enabled: m, disabled: x
# SPDIF out			enabled: s, disabled: x
# SPDIF in 			enabled: s, disabled: x
# ADAT out			enabled: a, disabled: x
# ADAT in			enabled: a, disabled: x
# DSD out			enabled: d, disabled: x
# e.g. 2Ai10o10xsxxx: Audio class 2.0, Asynchronous, input and output enabled (10 channels each), SPDIF output, no SPDIF input, no ADAT

# Supported build configs (Note these make use of the defaults in xua_conf.h)

#
# Asynchronous Mode Configs
#
# Audio Class 2, 10xInput, 10xOutput, no MIDI, no SPDIF
XCC_FLAGS_2Ai10o10xxxxxx = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2Ai10o10xxxxxx = 

# Audio Class 2, 10xInput, 10xOutput, no MIDI, SPDIF
XCC_FLAGS_2Ai10o10xsxxxx = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2Ai10o10xsxxxx = 

# Audio Class 1, 2xInput, 2xOutput, no MIDI, no S/PDIF
XCC_FLAGS_1Ai2o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN=2 -DNUM_USB_CHAN_OUT=2
INCLUDE_ONLY_IN_1Ai2o2xxxxxx =

# Audio Class 2, Async, 10xInput, 10xOutput, MIDI, no S/PDIF
XCC_FLAGS_2Ai10o10mxxxxx = $(BUILD_FLAGS) -DMIDI=1
INCLUDE_ONLY_IN_2Ai10o10mxxxxx =

#
# Synchronous Mode Configs
#
# Audio Class 1, Sync, 2xInput, 2xOutput, no MIDI, no S/PDIF
XCC_FLAGS_1Si2o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DXUA_SYNCMODE=3
INCLUDE_ONLY_IN_1Si2o2xxxxxx =

# Audio Class 2, Sync, 10xInput, 10xOutput, no MIDI, no S/PDIF
XCC_FLAGS_2Si10o10xxxxxx = $(BUILD_FLAGS) -DXUA_SYNCMODE=3
INCLUDE_ONLY_IN_2Si10o10xxxxxx =


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common

