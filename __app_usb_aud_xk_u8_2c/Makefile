# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk_usb_audio_u8_2c.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -DFLASH_MAX_UPGRADE_SIZE=64*1024*3 -fcomment-asm -Xmapper --map -Xmapper MAPFILE -Wall -O3 -report -lflash -fsubword-select -save-temps -g -fxscope -DXSCOPE -DXUD_SERIES_SUPPORT=1
#-fschedule

# The USED_MODULES variable lists other module used by the application. These
# modules will extend the SOURCE_DIRS, INCLUDE_DIRS and LIB_DIRS variables. 
# Modules are expected to be in the directory above the BASE_DIR directory.
USED_MODULES = module_usb_shared module_xud module_usb_audio module_spdif_tx module_spdif_rx module_usb_midi module_dfu module_i2c_shared module_usb_device module_locks module_i2c_simple

MODULE_LIBRARIES = xud_u

# Test build configs (Note these make use of the defaults in customdefines.h)

MFI ?= 0

ifeq ($(MFI), 0)

# Audio Class 2, Input, Output, No MIDI, SPDIF
XCC_FLAGS_2ioxs = $(BUILD_FLAGS) 
INCLUDE_ONLY_IN_2ioxs = 

# Audio Class 2, No Input, Output, No Midi, No SPDIF, DSD
XCC_FLAGS_2xoxxd = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=0 -DDSD_CHANS_DAC=2 -DCHAN_BUFF_CTRL=1
INCLUDE_ONLY_IN_2xoxxd = 

# Audio Class 2, Input, Output, No Midi, SPDIF, DSD
XCC_FLAGS_2ioxsd = $(BUILD_FLAGS) -DSPDIF_TX=1 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2ioxsd = 

# Audio Class 2, No Input, Output, No Midi, SPDIF, DSD
XCC_FLAGS_2xoxsd = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=1 -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2xoxsd = 

# Audio Class 2, No Input, Output, No MIDI, SPDIF
XCC_FLAGS_2xoxs = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0
INCLUDE_ONLY_IN_2xoxs = 

# Audio Class 2, No Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2xoxx = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2xoxx = 

# Audio Class 2, No Input, Output, No MIDI, No SPDIF, power-save featured enabled
XCC_FLAGS_2xoxx_lp = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=0 -DCHAN_BUFF_CTRL
INCLUDE_ONLY_IN_2xoxx_lp = ./src/extensions/powersave

#Audio Class 2, Input, Output, MIDI, No SPDIF
XCC_FLAGS_2iomx = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2iomx = 

#Audio Class 2, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx = $(BUILD_FLAGS) -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx = 

#Audio Class 2, Input, no Output, no MIDI, No SPDIF
XCC_FLAGS_2ixxx = $(BUILD_FLAGS) -DNUM_USB_CHAN_OUT=0 -DI2S_CHANS_DAC=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ixxx = 

# Audio Class 1, Input, Output, No MIDI, SPDIF, 2in/2out
XCC_FLAGS_1ioxs = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=2 -DNUM_USB_CHAN_OUT=2 -DAUDIO_CLASS=1 -DFULL_SPEED_AUDIO_2=0
INCLUDE_ONLY_IN_1ioxs = 

#Audio Class 1, No Input, Output, No MIDI, SPDIF, 0in/2out
XCC_FLAGS_1xoxs = $(BUILD_FLAGS) -DNUM_USB_CHAN_IN=0 -DNUM_USB_CHAN_OUT=2 -DAUDIO_CLASS=1 -DFULL_SPEED_AUDIO_2=0
INCLUDE_ONLY_IN_1xoxs = 

#Multiple output format test builds
#Audio Class 2, Input, Output, No MIDI, SPDIF, 32bit/4byte, 24bit/3byte, 16/2byte output formats
XCC_FLAGS_2ioxs_32b4_24b3_16b2 = $(BUILD_FLAGS) -DOUTPUT_FORMAT_COUNT=3 \
	-DSTREAM_FORMAT_OUTPUT_1_RESOLUTION_BITS=32 -DHS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES=4 \
 	-DSTREAM_FORMAT_OUTPUT_2_RESOLUTION_BITS=24 -DHS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES=3 \
 	-DSTREAM_FORMAT_OUTPUT_3_RESOLUTION_BITS=16 -DHS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES=2
INCLUDE_ONLY_IN_2ioxs_32b4_24b3_16b2 = 

#Audio Class 2, Input, Output, No MIDI, SPDIF, 16bit/4byte, 24bit/4byte, 32/4byte output formats
XCC_FLAGS_2ioxs_32b4_24b4_16b2 = $(BUILD_FLAGS) -DOUTPUT_FORMAT_COUNT=3 \
	-DSTREAM_FORMAT_OUTPUT_1_RESOLUTION_BITS=16 -DHS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES=2 \
 	-DSTREAM_FORMAT_OUTPUT_2_RESOLUTION_BITS=24 -DHS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES=4 \
 	-DSTREAM_FORMAT_OUTPUT_3_RESOLUTION_BITS=32 -DHS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES=4
INCLUDE_ONLY_IN_2ioxs_32b4_24b4_16b2 = 

#Audio Class 2, Input, Output, No MIDI, SPDIF, 16bit/2byte/PCM, 24bit/4byte/PCM, 32/4byte/DSD output formats
XCC_FLAGS_2xoxs_16b2pcm_24b4pcm_32b4dsd = $(BUILD_FLAGS) -DOUTPUT_FORMAT_COUNT=3 -DDSD_CHANS_DAC=2 \
	-DSTREAM_FORMAT_OUTPUT_1_RESOLUTION_BITS=16 -DHS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES=2 \
 	-DSTREAM_FORMAT_OUTPUT_2_RESOLUTION_BITS=24 -DHS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES=4 \
 	-DSTREAM_FORMAT_OUTPUT_3_RESOLUTION_BITS=32 -DHS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES=4 -DSTREAM_FORMAT_OUTPUT_3_DATAFORMAT=0x80000000
INCLUDE_ONLY_IN_2xoxs_16b2pcm_24b4pcm_32b4dsd =

#Audio Class 2, Input, Output, No MIDI, SPDIF, 16bit/4byte/PCM, 32bit/4byte/DSD, 24/4byte/PCM output formats
XCC_FLAGS_2xoxs_16b4pcm_32b4dsd_24b4pcm = $(BUILD_FLAGS) -DOUTPUT_FORMAT_COUNT=3 -DDSD_CHANS_DAC=2 \
	-DSTREAM_FORMAT_OUTPUT_1_RESOLUTION_BITS=16 -DHS_STREAM_FORMAT_OUTPUT_1_SUBSLOT_BYTES=4 \
 	-DSTREAM_FORMAT_OUTPUT_2_RESOLUTION_BITS=32 -DHS_STREAM_FORMAT_OUTPUT_2_SUBSLOT_BYTES=4 -DSTREAM_FORMAT_OUTPUT_2_DATAFORMAT=0x80000000 \
 	-DSTREAM_FORMAT_OUTPUT_3_RESOLUTION_BITS=24 -DHS_STREAM_FORMAT_OUTPUT_3_SUBSLOT_BYTES=4 -DSTREAM_FORMAT_OUTPUT_3_DATAFORMAT=0x00000001
INCLUDE_ONLY_IN_2xoxs_16b4pcm_32b4dsd_24b4pcm =

#Audio Class 2, Input, Output, MIDI, No SPDIF, reboot interrupt handler based on switch
XCC_FLAGS_2iomx_reboot = $(BUILD_FLAGS) -DMIDI=1 -DSPDIF_TX=0 -DSW_INT_HANDLER=1
INCLUDE_ONLY_IN_2iomx_reboot = 

else
# MFi test build configs - iAP support enabled

# Audio Class 2, iAP enabled, No Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2xoxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2xoxx_mfi = 

# Audio Class 2, iAP enabled, No Input, Output, No MIDI, No SPDIF, power-save featured enabled
XCC_FLAGS_2xoxx_mfi_lp = $(BUILD_FLAGS) -DIAP=1 -DNUM_USB_CHAN_IN=0 -DI2S_CHANS_ADC=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2xoxx_mfi_lp = ./src/extensions/powersave

#Audio Class 2, iAP enabled, Input, Output, No MIDI, No SPDIF
XCC_FLAGS_2ioxx_mfi = $(BUILD_FLAGS) -DIAP=1 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2ioxx_mfi = 

#Audio Class 2, iAP enabled, Input, Output, MIDI, No SPDIF
XCC_FLAGS_2iomx_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=1 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2iomx_mfi = 

#Audio Class 2, iAP enabled, Input, Output, MIDI, No SPDIF. Select USB A port. Turn on reboot based on switch. Ignore VBUS.
#Note, this is the config used for Apple role-switch
XCC_FLAGS_2iomx_usba_reboot_mfi = $(BUILD_FLAGS) -DIAP=1 -DMIDI=1 -DSPDIF_TX=0 -DUSB_SEL_A=1 -DSW_INT_HANDLER=1 -DSWITCH_VAL=0b1000 -DXUD_PWR_CFG=0
INCLUDE_ONLY_IN_2iomx_usba_reboot_mfi = 

include mfi.mk

endif

ifeq ($(TEST_CONFIGS),1)
XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2

endif

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

XMOS_MAKE_PATH ?= ../..
include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
