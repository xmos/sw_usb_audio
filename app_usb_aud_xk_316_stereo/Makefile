# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-316-stereo.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -fcomment-asm -O3 -report -lquadflash -g -fxscope -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xua lib_i2c

# Build config naming scheme:
#
# Audio Class:   1 or 2
# Sync Mode      A(sync) or S(ync)
# I2S            M(aster) or S(lave)
# Input          enabled: i (channelcount)
# Output         enabled: o (channelcount)
# MIDI           enabled: m, disabled: x
# SPDIF in       enabled: s, disabled: x
# SPDIF out      enabled: s, disabled: x
# ADAT in        enabled: a, disabled: x
# ADAT out       enabled: a, disabled: x
# DSD out        enabled: d, disabled: x
#
# e.g. 2AMi10o10xxsxxx: Audio class 2.0, Asynchronous, I2S Master, input and output enabled (10 channels each), no MIDI, SPDIF output, no SPDIF input, no ADAT

#
# Supported build configs (Note these make use of the defaults in xua_conf.h)
#

#
# Asynchronous Mode Configs
#

# Audio Class 1

# Audio Class 1, Async, I2S Master, 2xInput, 2xOutput
INCLUDE_ONLY_IN_1AMi2o2xxxxxx =
XCC_FLAGS_1AMi2o2xxxxxx = $(BUILD_FLAGS)        -DAUDIO_CLASS=1

# Audio Class 1, Async, I2S Master, 2xInput, 2xOutput, S/PDIF Tx (copy of audio data to I2S)
INCLUDE_ONLY_IN_1AMi2o2xxsxxx =
XCC_FLAGS_1AMi2o2xxsxxx = $(BUILD_FLAGS)        -DAUDIO_CLASS=1 \
                                                -DXUA_SPDIF_TX_EN=1 \
                                                -DNUM_USB_CHAN_OUT=2

# Audio Class 2

# Audio Class 2, Async, I2S Master, 2xInput, 2xOutput
INCLUDE_ONLY_IN_2AMi2o2xxxxxx =
XCC_FLAGS_2AMi2o2xxxxxx = $(BUILD_FLAGS)

# Audio Class 2, Async, I2S Master, 2xInput, 2xOutput, S/PDIF Tx (copy of audio data to I2S)
INCLUDE_ONLY_IN_2AMi2o2xxsxxx = 
XCC_FLAGS_2AMi2o2xxsxxx = $(BUILD_FLAGS)        -DXUA_SPDIF_TX_EN=1 \
                                                -DNUM_USB_CHAN_OUT=2

# Audio Class 2, Async, I2S Master, 2xInput, 2xOutput, 48kHz ONLY
INCLUDE_ONLY_IN_2AMi2o2xxxxxx_48 = 
XCC_FLAGS_2AMi2o2xxxxxx_48 = $(BUILD_FLAGS)     -DMAX_FREQ=48000 \
                                                -DMIN_FREQ=48000

ifneq ($(CONFIG),)
BUILD_TEST_CONFIGS = 1
endif

BUILD_TEST_CONFIGS ?= 0
ifeq ($(BUILD_TEST_CONFIGS),1)
include configs_build.inc
PARTIAL_TEST_CONFIGS = 1
endif

PARTIAL_TEST_CONFIGS ?= 0
ifeq ($(PARTIAL_TEST_CONFIGS),1)
include configs_partial.inc
endif

TEST_SUPPORT_CONFIGS ?= 0
ifeq ($(TEST_SUPPORT_CONFIGS),1)
include configs_test.inc
endif


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
