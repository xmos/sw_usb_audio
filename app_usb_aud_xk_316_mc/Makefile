# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-316-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -O3 -report -lquadflash -g -fxscope -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xua lib_xud lib_spdif lib_i2c lib_adat

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

# Supported build configs (Note these make use of the defaults in xua_conf.h)

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2i10o10xxxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0
INCLUDE_ONLY_IN_2i10o10xxxxxx = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2i10o10xsxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2i10o10xsxxxx = 

XCC_FLAGS_1i2o2xxxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN=2 -DNUM_USB_CHAN_OUT=2
INCLUDE_ONLY_IN_1i2o2xxxxxx =

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common

