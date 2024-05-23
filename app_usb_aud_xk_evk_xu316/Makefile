# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = XK-EVK-XU316
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lquadflash -g -fxscope -DXSCOPE -DUSB_TILE=tile[0] -DXUA_QUAD_SPI_FLASH=1 -DADAT_TX_USE_SHARED_BUFF=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_sw_pll lib_xua lib_i2c

# Build config naming scheme:

# Audio Class:  1 or 2
# Sync Mode     A(sync), S(ync) or (a)D(aptive)
# I2S           M(aster), S(lave) or X (I2S disabled)
# Input         enabled: i (channelcount)
# Output        enabled: o (channelcount)
# MIDI          enabled: m, disabled: x
# SPDIF in      enabled: s, disabled: x
# SPDIF out     enabled: s, disabled: x
# ADAT in       enabled: a, disabled: x
# ADAT out      enabled: a, disabled: x
# DSD out       enabled: d, disabled: x
# e.g. 2AMi10o10xxsxxx: Audio class 2.0, Asynchronous, I2S Master, input and output enabled (10 channels each), no MIDI, SPDIF output, no SPDIF input, no ADAT

# Fully tested build configs (Note these make use of the defaults in xua_conf.h)

# Audio Class 1, Async, I2S Master, 2xInput, 2xOutput
XCC_FLAGS_1AMi2o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1
INCLUDE_ONLY_IN_1AMi2o2xxxxxx =

# Audio Class 2, Async, I2S Master, 2xInput, 2xOutput
XCC_FLAGS_2AMi2o2xxxxxx = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2AMi2o2xxxxxx =


TEST_SUPPORT_CONFIGS ?= 0
ifeq ($(TEST_SUPPORT_CONFIGS),1)
include configs_test.inc
endif


#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
