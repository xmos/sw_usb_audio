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

# Audio Class:  	1 or 2
# Sync Mode 		A(sync)/S(ync)
# I2S 				M(aster)/S(lave)
# Input 			enabled: i (channelcount)
# Output 			enabled: o (channelcount)
# MIDI 				enabled: m, disabled: x
# SPDIF in 			enabled: s, disabled: x
# SPDIF out			enabled: s, disabled: x
# ADAT in			enabled: a, disabled: x
# ADAT out			enabled: a, disabled: x
# DSD out			enabled: d, disabled: x
# e.g. 2AMi10o10xxsxxx: Audio class 2.0, Asynchronous, I2S Master, input and output enabled (10 channels each), SPDIF output, no SPDIF input, no ADAT

# Supported build configs (Note these make use of the defaults in xua_conf.h)

#
# Asynchronous Mode Configs
#
# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx = 

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2ASi8o8xxxxxx = $(BUILD_FLAGS)		-DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi8o8xxxxxx =

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput, TDM
XCC_FLAGS_2ASi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)	-DCODEC_MASTER=1 \
												-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DMAX_FREQ=96000
INCLUDE_ONLY_IN_2ASi8o8xxxxxx_tdm8 =


# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, TDM
# TODO can run at 192kHz when AppPLL settings for 49MHz added
XCC_FLAGS_2AMi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DMAX_FREQ=96000
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_tdm8 = 

# Audio Class 2, Async, I2S Master, 32xInput, 32xOutput, TDM
XCC_FLAGS_2AMi32o32xxxxxx_tdm8 = $(BUILD_FLAGS)	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DNUM_USB_CHAN_OUT=32 \
												-DI2S_CHANS_DAC=32 \
												-DNUM_USB_CHAN_IN=32 \
												-DI2S_CHANS_ADC=32 \
												-DMAX_FREQ=48000
INCLUDE_ONLY_IN_2AMi32o32xxxxxx_tdm8 = 


# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx
XCC_FLAGS_2AMi8o10xxsxxx = $(BUILD_FLAGS)		-DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2AMi8o10xxsxxx =

# Audio Class 1, Async, I2S Master, 2xInput, 2xOutput
XCC_FLAGS_1AMi2o2xxxxxx = $(BUILD_FLAGS) 		-DAUDIO_CLASS=1 \
						 						-DNUM_USB_CHAN_IN=2 \
												-DNUM_USB_CHAN_OUT=2
INCLUDE_ONLY_IN_1AMi2o2xxxxxx =

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, MIDI
XCC_FLAGS_2AMi8o8mxxxxx = $(BUILD_FLAGS)		-DMIDI=1
INCLUDE_ONLY_IN_2AMi8o8mxxxxx =

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
XCC_FLAGS_2AMi10o10xssxxx = $(BUILD_FLAGS)		-DXUA_SPDIF_TX_EN=1 \
						   						-DXUA_SPDIF_RX_EN=1
INCLUDE_ONLY_IN_2AMi10o10xssxxx =

# Audio Class 2, Async, I2S Slave, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
XCC_FLAGS_2ASi10o10xssxxx = $(BUILD_FLAGS)		-DXUA_SPDIF_TX_EN=1 \
						   						-DXUA_SPDIF_RX_EN=1 \
												-DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi10o10xssxxx =

# Audio Class 2, Async, I2S Master, 10xInput, 8xOutput, S/PDIF Rx
XCC_FLAGS_2AMi10o8xsxxxx = $(BUILD_FLAGS) 		-DXUA_SPDIF_RX_EN=1
INCLUDE_ONLY_IN_2AMi10o8xsxxxx =

# Audio Class 2, Async, I2S Master, 16xInput, 8xOutput, ADAT Rx
XCC_FLAGS_2AMi16o8xxxaxx = $(BUILD_FLAGS) 		-DXUA_ADAT_RX_EN=1
INCLUDE_ONLY_IN_2AMi16o8xxxaxx =

# Audio Class 2, Async, I2S master, 8xInput, 16xOutput, ADAT Tx
XCC_FLAGS_2AMi8o16xxxxax = $(BUILD_FLAGS) 		-DXUA_ADAT_TX_EN=1
INCLUDE_ONLY_IN_2AMi8o16xxxxax =

#
# Synchronous Mode Configs
#
# Audio Class 1, Sync, I2S Master, 2xInput, 2xOutput
XCC_FLAGS_1SMi2o2xxxxxx = $(BUILD_FLAGS)		-DAUDIO_CLASS=1 \
						 						-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC
INCLUDE_ONLY_IN_1SMi2o2xxxxxx =

# Audio Class 2, Sync, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS)		-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC
INCLUDE_ONLY_IN_2SMi8o8xxxxxx =

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput, TDM
# (1024x Mclk required for 192/176 TDM)
XCC_FLAGS_2SMi10o10xxxxxx_tdm8 = $(BUILD_FLAGS)	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
												-DMCLK_48=1024*48000 \
												-DMCLK_441=1024*44100
INCLUDE_ONLY_IN_2SMi10o10xxxxxx_tdm8 = 


ifeq ($(TEST_CONFIGS),1)
XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2
endif

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common

