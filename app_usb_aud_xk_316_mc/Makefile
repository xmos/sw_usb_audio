# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-316-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -fcomment-asm -O3 -report -lquadflash -g -fxscope -DUSB_TILE=tile[0] -DADAT_TX_USE_SHARED_BUFF=1 -DXUA_QUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_sw_pll lib_xua lib_i2c

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

# Audio Class 1, Async, I2S Master, 2xInput, 2xOutput
INCLUDE_ONLY_IN_1AMi2o2xxxxxx =
XCC_FLAGS_1AMi2o2xxxxxx = $(BUILD_FLAGS)        -DAUDIO_CLASS=1

# Audio Class 2, Async, I2S Master, 2xInput, 2xOutput
INCLUDE_ONLY_IN_2AMi2o2xxxxxx =
XCC_FLAGS_2AMi2o2xxxxxx = $(BUILD_FLAGS)        -DI2S_CHANS_DAC=2 \
                                                -DI2S_CHANS_ADC=2

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
INCLUDE_ONLY_IN_2AMi8o8xxxxxx =
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, Mixer
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_mix8 =
XCC_FLAGS_2AMi8o8xxxxxx_mix8 = $(BUILD_FLAGS)   -DMAX_MIX_COUNT=8

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, TDM
# TODO can run at 192kHz when AppPLL settings for 49MHz added
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_tdm8 =
XCC_FLAGS_2AMi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)   -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=96000

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput, TDM
INCLUDE_ONLY_IN_2ASi8o8xxxxxx_tdm8 =
XCC_FLAGS_2ASi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)   -DCODEC_MASTER=1 \
                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=96000

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, MIDI
INCLUDE_ONLY_IN_2AMi8o8mxxxxx =
XCC_FLAGS_2AMi8o8mxxxxx = $(BUILD_FLAGS)		-DMIDI=1

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
INCLUDE_ONLY_IN_2AMi10o10xssxxx =
XCC_FLAGS_2AMi10o10xssxxx = $(BUILD_FLAGS)      -DXUA_SPDIF_TX_EN=1 \
                                                -DXUA_SPDIF_RX_EN=1

# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, ADAT Tx, ADAT Rx
INCLUDE_ONLY_IN_2AMi16o16xxxaax =
XCC_FLAGS_2AMi16o16xxxaax = $(BUILD_FLAGS)      -DXUA_ADAT_TX_EN=1 -DXUA_ADAT_RX_EN=1

# Audio Class 2, Async, I2S Master, 18xInput, 18xOutput, ADAT Tx, ADAT Rx, S/PDIF Tx, S/PDIF Rx
INCLUDE_ONLY_IN_2AMi18o18mssaax =
XCC_FLAGS_2AMi18o18mssaax = $(BUILD_FLAGS)      -DMIDI=1 -DXUA_ADAT_TX_EN=1 -DXUA_ADAT_RX_EN=1 -DXUA_SPDIF_TX_EN=1 -DXUA_SPDIF_RX_EN=1 -DMAX_FREQ=96000

#
# Synchronous Mode Configs
#
# Audio Class 1, Sync, I2S Master, 2xInput, 2xOutput
INCLUDE_ONLY_IN_1SMi2o2xxxxxx =
XCC_FLAGS_1SMi2o2xxxxxx = $(BUILD_FLAGS)        -DAUDIO_CLASS=1 \
                                                -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC

# Audio Class 2, Sync, I2S Master, 8xInput, 8xOutput
INCLUDE_ONLY_IN_2SMi8o8xxxxxx =
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS)        -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC

# Audio Class 2, Sync, I2S Slave, 8xInput, 8xOutput
INCLUDE_ONLY_IN_2SSi8o8xxxxxx =
XCC_FLAGS_2SSi8o8xxxxxx = $(BUILD_FLAGS)        -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
                                                -DCODEC_MASTER=1

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
