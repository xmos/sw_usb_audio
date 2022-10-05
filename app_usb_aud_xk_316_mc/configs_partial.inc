# Configs that have been partially tested, but not as comprehensively as those in the Makefile

#
# Asynchronous Mode Configs
#
# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)		
INCLUDE_ONLY_IN_2AMi8o8xxxxxx = 

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2ASi8o8xxxxxx = $(BUILD_FLAGS)		-DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi8o8xxxxxx =

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
# Audio Class 2, Sync, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS)		-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC
INCLUDE_ONLY_IN_2SMi8o8xxxxxx =

# Audio Class 2, Sync, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2SSi8o8xxxxxx = $(BUILD_FLAGS)		-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
						  						-DCODEC_MASTER=1
INCLUDE_ONLY_IN_2SSi8o8xxxxxx =

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput, TDM
# (1024x Mclk required for 192/176 TDM)
XCC_FLAGS_2SMi10o10xxxxxx_tdm8 = $(BUILD_FLAGS)	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
												-DMCLK_48=1024*48000 \
												-DMCLK_441=1024*44100
INCLUDE_ONLY_IN_2SMi10o10xxxxxx_tdm8 = 

