# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = XK-EVK-XU316
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lquadflash -g -fxscope -DXSCOPE -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1 -DUAC_FORCE_FEEDBACK_EP=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xud lib_xua lib_i2c lib_i2s


# Build config naming scheme:

# Audio Class:  1 or 2
# Input         enabled: i (channelcount)
# Output        enabled: o (channelcount)
# MIDI          enabled: m, disabled: x
# SPDIF out     enabled: s, disabled: x
# SPDIF in      enabled: s, disabled: x
# ADAT out      enabled: a, disabled: x
# ADAT in       enabled: a, disabled: x
# DSD out       enabled: d, disabled: x
# e.g. 2i10o10xsxxx: Audio class 2.0, input and output enabled (10 channels each), SPDIF output, no SPDIF input, no ADAT

# Configs that have only had their build process tested

# Audio Class 1, 2 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_1i2o2 = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DMIN_FREQ=44100 -DMAX_FREQ=48000 -DI2S_CHANS_ADC=2 -DI2S_CHANS_DAC=2 -DNUM_USB_CHAN_OUT=2 -DNUM_USB_CHAN_IN=2 -DNUM_USB_CHAN_OUT=2 -DNUM_USB_CHAN_IN=2 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_1i2o2 =

# Audio Class 2, 2 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_2i2o2 = $(BUILD_FLAGS) -DMIN_FREQ=44100 -DMAX_FREQ=192000 -DI2S_CHANS_ADC=2 -DI2S_CHANS_DAC=2 -DNUM_USB_CHAN_OUT=2 -DNUM_USB_CHAN_IN=2 -DNUM_USB_CHAN_OUT=2 -DNUM_USB_CHAN_IN=2 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2i2o2 =

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
