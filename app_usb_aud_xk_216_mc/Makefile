# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-216-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
# The EXTRA_BUILD_FLAGS variable can be used on the xmake command line to add options
BUILD_FLAGS    = $(EXTRA_BUILD_FLAGS) -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -O3 -report -lquadflash -g -fxscope -march=xs2a -DUSB_TILE=tile[1] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = lib_xua lib_xud lib_spdif lib_i2c lib_adat

# Build config naming scheme:

# Audio Class:  1 or 2
# Sync Mode 	A(sync) or S(ync)
# Input 		enabled: i (channelcount)
# Output 		enabled: o (channelcount)
# MIDI 			enabled: m, disabled: x
# SPDIF out		enabled: s, disabled: x
# SPDIF in 		enabled: s, disabled: x
# ADAT out		enabled: a, disabled: x
# ADAT in		enabled: a, disabled: x
# DSD out		enabled: d, disabled: x
# e.g. 2Ai10o10xsxxx: Audio class 2.0, Asynchronous, input and output enabled (10 channels each), SPDIF output, no SPDIF input, no ADAT

TEST_DFU_1 ?= 0
ifeq ($(TEST_DFU_1),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9901
endif
TEST_DFU_2 ?= 0
ifeq ($(TEST_DFU_2),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9902
endif

# Test build configs (Note these make use of the defaults in xua_conf.h)

# Audio Class 2, Input (8), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM mode
XCC_FLAGS_2Ai8o8xxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8 \
								-DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 
INCLUDE_ONLY_IN_2Ai8o8xxxxx_tdm8 =

# Audio Class 2, Input (8), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM slave mode
XCC_FLAGS_2Ai8o8xxxxx_tdm8_slave  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8 \
								-DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DMIXER=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2Ai8o8xxxxx_tdm8_slave =


# Audio Class 2, Input (0), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM slave mode
XCC_FLAGS_2Ai0o8xxxxx_tdm8_slave  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=0 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=0 \
								-DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DMIXER=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2Ai0o8xxxxx_tdm8_slave =



# Audio Class 2, Input (16), Output (16), No MIDI, No SPDIF i/o, No ADAT i/o, No DSD, TDM mode
# Note: sample rate restricted to 96K to fit in USB bandwidth
XCC_FLAGS_2Ai16o16xxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=16 -DI2S_CHANS_ADC=16 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16 \
								-DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2Ai16o16xxxxx_tdm8  =

# Audio Class 2, Input, Output, No MIDI, No SPDIF Tx, TDM (32in/32out)
XCC_FLAGS_2Ai32o32xxxxx_tdm8  = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2Ai32o32xxxxx_tdm8 =

# Audio Class 2, Input, Output, No MIDI, SPDIF, TDM (32in/32out)
XCC_FLAGS_2Ai32o32xsxxx_tdm8 = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2Ai32o32xsxxx_tdm8  =

# Audio Class 2, Input, Output, MIDI, SPDIF
XCC_FLAGS_2Ai10o10msxxxx = $(BUILD_FLAGS) -DMIDI=1 -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2Ai10o10msxxxx = 

# Audio Class 2, Input, Output, MIDI, SPDIF, DSD
XCC_FLAGS_2Ai10o10xxxxxd = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2Ai10o10xxxxxd = 

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2Ai10o10xxxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0
INCLUDE_ONLY_IN_2Ai10o10xxxxxx = 

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2Ai10o10xxxxxx_slave = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2Ai10o10xxxxxx_slave = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2Ai10o10xsxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2Ai10o10xsxxxx = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2Ai10o10xsxxxx_mix8 = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=1 -DMAX_MIX_COUNT=8
INCLUDE_ONLY_IN_2Ai10o10xsxxxx_mix8 = 

# Audio Class 2, Input, Output, No Midi, SPDIF, DSD
XCC_FLAGS_2Ai10o10xsxxxd = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2Ai10o10xsxxxd = 

# Audio Class 2, 10 Input, 16 Output, no MIDI, no SPDIF tx, no SPDIF Rx, ADAT tx, no ADAT rx, no DSD
XCC_FLAGS_2Ai10o16xxxaxx = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=0 -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16
INCLUDE_ONLY_IN_2Ai10o16xxxaxx = 

# Audio Class 2, 16 Input, 10 Output, no MIDI, no SPDIF tx, no SPDIF Rx, ADAT tx, ADAT rx, no DSD
# Sample rate restriced to 96kHz fit in USB bandwidth
XCC_FLAGS_2Ai16o16xxxaax = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=0 -DMIDI=0 -DADAT_RX=1 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16
INCLUDE_ONLY_IN_2Ai16o16xxxaax = 

# Audio Class 2, Input, Output, No MIDI, SPDIF out, SPDIF in
XCC_FLAGS_2Ai10o10xssxxx = $(BUILD_FLAGS) -DSPDIF_RX=1
INCLUDE_ONLY_IN_2Ai10o10xssxxx = 

# Audio Class 1, 2 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_1Ai2o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1
INCLUDE_ONLY_IN_1Ai2o2xxxxxx =

# Audio Class 1, 8 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_1Ai8o2xxxxxx = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=0 -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN_FS=6 -DMAX_FREQ_FS=44100 -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16
INCLUDE_ONLY_IN_1Ai8o2xxxxxx =

# Audio Class 2, No I2S input, No I2S Output, SPDIF output 
XCC_FLAGS_2Ai0o2xsxxxx_noi2s = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 -DI2S_CHANS_ADC=0 -DI2S_CHANS_DAC=0 -DNUM_USB_CHAN_IN=0 -DNUM_USB_CHAN_OUT=2
INCLUDE_ONLY_IN_2Ai0o2xsxxxx_noi2s = 

# Audio Class 2, Synchronous, No Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2Si10o10xxxxxx = $(BUILD_FLAGS) -DMIDI=0 -DXUA_SPDIF_TX_EN=0 -DXUA_SYNCMODE=3
INCLUDE_ONLY_IN_2Si10o10xxxxxx = 

ifeq ($(TEST_CONFIGS),1)
XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2
endif

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
