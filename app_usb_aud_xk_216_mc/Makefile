# The TARGET variable determines what target system the application is
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-216-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -fcomment-asm -O3 -report -lquadflash -g -fxscope -march=xs2a -DBOARD_SUPPORT_BOARD=XK_AUDIO_216_MC_AB -DADAT_TX_USE_SHARED_BUFF=1 -DXUA_QUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables.
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xua lib_i2c lib_board_support

# Build config naming scheme:

# Audio Class:  1 or 2
# Sync Mode             A(sync), S(ync) or (a)D(aptive)
# I2S                   M(aster), S(lave) or X (I2S disabled)
# Input                 enabled: i (channelcount)
# Output                enabled: o (channelcount)
# MIDI                  enabled: m, disabled: x
# S/PDIF in             enabled: s, disabled: x
# S/PDIF out            enabled: s, disabled: x
# ADAT in               enabled: a, disabled: x
# ADAT out              enabled: a, disabled: x
# DSD out               enabled: d, disabled: x
#
# e.g. 2AMi10o10xsxxx: Audio class 2.0, Asynchronous, I2S Master,input and output enabled (10 channels each), no MIDI, S/PDIF output, no S/PDIF input, no ADAT

# Fully tested build configs (Note these make use of the defaults in xua_conf.h)

# Audio Class 2, I2S Master, 10xInput, 10xOutput, S/PDIF Rx, S/PDIF Tx
INCLUDE_ONLY_IN_2AMi10o10xssxxx =
XCC_FLAGS_2AMi10o10xssxxx = $(BUILD_FLAGS)      -DXUA_SPDIF_RX_EN=1 \
                                                -DXUA_SPDIF_TX_EN=1

# Audio Class 2, I2S Slave, 10xInput, 10xOutput, S/PDIF Rx, S/PDIF Tx
INCLUDE_ONLY_IN_2ASi10o10xssxxx =
XCC_FLAGS_2ASi10o10xssxxx = $(BUILD_FLAGS)      -DXUA_SPDIF_RX_EN=1 \
                                                -DXUA_SPDIF_TX_EN=1 \
                                                -DCODEC_MASTER=1

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, MIDI, S/PDIF Tx
INCLUDE_ONLY_IN_2AMi8o10mxsxxx =
XCC_FLAGS_2AMi8o10mxsxxx = $(BUILD_FLAGS) 		-DMIDI=1 \
												-DXUA_SPDIF_TX_EN=1

# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, ADAT Tx, ADAT Rx
INCLUDE_ONLY_IN_2AMi16o16xxxaax =
XCC_FLAGS_2AMi16o16xxxaax = $(BUILD_FLAGS)      -DXUA_ADAT_TX_EN=1 -DXUA_ADAT_RX_EN=1

# Audio Class 2, Async, I2S Master, 18xInput, 18xOutput, ADAT Tx, ADAT Rx, S/PDIF Tx, S/PDIF Rx
INCLUDE_ONLY_IN_2AMi18o18mssaax =
XCC_FLAGS_2AMi18o18mssaax = $(BUILD_FLAGS)      -DMIDI=1 -DXUA_ADAT_TX_EN=1 -DXUA_ADAT_RX_EN=1 -DXUA_SPDIF_TX_EN=1 -DXUA_SPDIF_RX_EN=1 -DMAX_FREQ=96000

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
