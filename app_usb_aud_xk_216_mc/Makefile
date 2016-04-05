# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk-audio-216-mc.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lquadflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DSDA_HIGH=2 -DSCL_HIGH=1 -DXUD_SERIES_SUPPORT=4 -march=xs2a -DUSB_TILE=tile[1] -DADAT_TX_USE_SHARED_BUFF=1 -DQUAD_SPI_FLASH=1

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_usb_device module_i2c_shared module_i2c_single_port module_adat_tx module_adat_rx

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

TEST_DFU_1 ?= 0
ifeq ($(TEST_DFU_1),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9901
endif
TEST_DFU_2 ?= 0
ifeq ($(TEST_DFU_2),1)
BUILD_FLAGS += -DBCD_DEVICE=0x9902
endif

MFI ?= 0

ifeq ($(MFI), 0)

# Test build configs (Note these make use of the defaults in customdefines.h)

# Audio Class 2, Input (8), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM mode
XCC_FLAGS_2i8o8xxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8 \
								-DMIDI=0 -DSPDIF_TX=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 
INCLUDE_ONLY_IN_2i8o8xxxxx_tdm8 =

# Audio Class 2, Input (8), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM slave mode
XCC_FLAGS_2i8o8xxxxx_tdm8_slave  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=8 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=8 \
								-DMIDI=0 -DSPDIF_TX=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DMIXER=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2i8o8xxxxx_tdm8_slave =


# Audio Class 2, Input (0), Output (8), No MIDI, No SPDIF i/o, No ADAT i/o, TDM slave mode
XCC_FLAGS_2i0o8xxxxx_tdm8_slave  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=8 -DI2S_CHANS_ADC=0 -DNUM_USB_CHAN_OUT=8 -DNUM_USB_CHAN_IN=0 \
								-DMIDI=0 -DSPDIF_TX=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000 -DMIXER=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2i0o8xxxxx_tdm8_slave =



# Audio Class 2, Input (16), Output (16), No MIDI, No SPDIF i/o, No ADAT i/o, No DSD, TDM mode
# Note: sample rate restricted to 96K to fit in USB bandwidth
XCC_FLAGS_2i16o16xxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=16 -DI2S_CHANS_ADC=16 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16 \
								-DMIDI=0 -DSPDIF_TX=0 -DSPDIF_RX=0 -DADAT_TX=0 -DADAT_RX=0 -DDSD_CHANS_DAC=0 \
								-DI2S_MODE_TDM=1 -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2i16o16xxxxx_tdm8  =

# Audio Class 2, Input, Output, No MIDI, No SPDIF Tx, TDM (32in/32out)
XCC_FLAGS_2i32o32xxxxx_tdm8  = $(BUILD_FLAGS) -DSPDIF_TX=0 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2i32o32xxxxx_tdm8 =

# Audio Class 2, Input, Output, No MIDI, SPDIF, TDM (32in/32out)
XCC_FLAGS_2i32o32xsxxx_tdm8 = $(BUILD_FLAGS) -DSPDIF_TX=1 -DI2S_MODE_TDM=1 -DI2S_CHANS_ADC=32 -DMAX_FREQ=48000 -DI2S_CHANS_DAC=32 -DNUM_USB_CHAN_OUT=32 -DNUM_USB_CHAN_IN=32
INCLUDE_ONLY_IN_2i32o32xsxxx_tdm8  =

# Audio Class 2, Input, Output, MIDI, SPDIF
XCC_FLAGS_2i10o10msxxxx = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF_TX=1
INCLUDE_ONLY_IN_2i10o10msxxxx = 

# Audio Class 2, Input, Output, MIDI, SPDIF, DSD
XCC_FLAGS_2i10o10xxxxxd = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=0 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2i10o10xxxxxd = 

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2i10o10xxxxxx = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2i10o10xxxxxx = 

# Audio Class 2, Input, Output, no MIDI, no SPDIF
XCC_FLAGS_2i10o10xxxxxx_slave = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=0 -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2i10o10xxxxxx_slave = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2i10o10xsxxxx = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=1
INCLUDE_ONLY_IN_2i10o10xsxxxx = 

# Audio Class 2, Input, Output, no MIDI, SPDIF
XCC_FLAGS_2i10o10xsxxxx_mix8 = $(BUILD_FLAGS) -DMIDI=0 -DSPDIF_TX=1 -DMAX_MIX_COUNT=8
INCLUDE_ONLY_IN_2i10o10xsxxxx_mix8 = 

# Audio Class 2, Input, Output, No Midi, SPDIF, DSD
XCC_FLAGS_2i10o10xsxxxd = $(BUILD_FLAGS) -DSPDIF_TX=1 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2i10o10xsxxxd = 

# Audio Class 2, 10 Input, 16 Output, no MIDI, no SPDIF tx, no SPDIF Rx, ADAT tx, no ADAT rx, no DSD
XCC_FLAGS_2i10o16xxxaxx = $(BUILD_FLAGS) -DSPDIF_TX=0 -DMIDI=0 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16
INCLUDE_ONLY_IN_2i10o16xxxaxx = 

# Audio Class 2, 16 Input, 10 Output, no MIDI, no SPDIF tx, no SPDIF Rx, ADAT tx, ADAT rx, no DSD
# Sample rate restriced to 96kHz fit in USB bandwidth
XCC_FLAGS_2i16o16xxxaax = $(BUILD_FLAGS) -DSPDIF_TX=0 -DMIDI=0 -DADAT_RX=1 -DADAT_TX=1 -DMAX_FREQ=96000 -DNUM_USB_CHAN_OUT=16 -DNUM_USB_CHAN_IN=16
INCLUDE_ONLY_IN_2i16o16xxxaax = 

# Audio Class 2, Input, Output, No MIDI, SPDIF out, SPDIF in
XCC_FLAGS_2i10o10xssxxx = $(BUILD_FLAGS) -DSPDIF_RX=1
INCLUDE_ONLY_IN_2i10o10xssxxx = 

# Audio Class 1, 2 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_1i2o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1
INCLUDE_ONLY_IN_1i2o2xxxxxx =

# Audio Class 1, 8 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_1i8o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 -DNUM_USB_CHAN_IN_FS=6 -DMAX_FREQ_FS=44100 -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16
INCLUDE_ONLY_IN_1i8o2xxxxxx =

ifeq ($(TEST_CONFIGS),1)
XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2
endif

else

# MFi test build configs - iAP support enabled
	
# # Audio Class 2, iAP enabled, Input, Output, No MIDI, SPDIF Tx
XCC_FLAGS_2i10o10xsxxxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DSPDIF_TX=1 -DMIDI=0
INCLUDE_ONLY_IN_2i10o10xsxxxx_mfi = 

# # Audio Class 2, iAP enabled, No Input, Output, No MIDI, SPDIF Tx, DSD
XCC_FLAGS_20i10oxsxxxxd_mfi = $(BUILD_FLAGS) -DIAP=1 -DSPDIF_TX=1 -DMIDI=0 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_20i10oxsxxxxd_mfi = 

#Audio Class 2, iAP enabled, EA Protocol (Native Transport), Input, Output, No MIDI, No SPDIF Tx. i
# Hid controls disabled (buttons used for EA)
# XCC_FLAGS_210i10oxxxxx_mfi_n = $(BUILD_FLAGS) -DIAP=1 -DIAP_EA_NATIVE_TRANS=1 -DMIDI=0 -DSPDIF_TX=0 -DHID_CONTROLS=0
# INCLUDE_ONLY_IN_210i10oxxxxx_mfi_n =

#Audio Class 2, iAP enabled, Input, Output, No,  No SPDIF Tx. Select USB A port. Ignore VBUS.
#Note, this is the config used for Apple role-switch
XCC_FLAGS_2ioxx_usba_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=0 -DSPDIF_TX=0 -DUSB_SEL_A=1 -DXUD_PWR_CFG=0
INCLUDE_ONLY_IN_2ioxx_usba_mfi = 

include mfi.mk

endif


MODULE_LIBRARIES = xud_x200

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
