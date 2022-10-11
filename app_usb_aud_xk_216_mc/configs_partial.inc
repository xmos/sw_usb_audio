# Configs that have been partially tested, but not as comprehensively as those in the Makefile

# Audio Class 2, Async, I2S Master, 8xInput 8xOutput (TDM)
INCLUDE_ONLY_IN_2AMi8o8xxxxx_tdm8 =
XCC_FLAGS_2AMi8o8xxxxx_tdm8 = $(BUILD_FLAGS) 	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DMAX_FREQ=96000

# Audio Class 2, Async, I2S Slave, 8xInput 8xOutput (TDM)
INCLUDE_ONLY_IN_2ASi8o8xxxxx_tdm8 =
XCC_FLAGS_2ASi8o8xxxxx_tdm8 = $(BUILD_FLAGS) 	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DMAX_FREQ=96000 \
												-DCODEC_MASTER=1

# Audio Class 2, Async, I2S Master, 32xInput 32xOutput (TDM)
INCLUDE_ONLY_IN_2AMi32o32xxxxx_tdm8 = 
XCC_FLAGS_2AMi32o32xxxxx_tdm8 = $(BUILD_FLAGS) 	-DI2S_CHANS_ADC=32 \
												-DI2S_CHANS_DAC=32 \
												-DNUM_USB_CHAN_IN=32 \
												-DNUM_USB_CHAN_OUT=32 \
												-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DMAX_FREQ=48000

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, MIDI, S/PDIF Tx
INCLUDE_ONLY_IN_2AMi8o10mxsxxx =  
XCC_FLAGS_2AMi8o10mxsxxx = $(BUILD_FLAGS) 		-DMIDI=1 \
												-DXUA_SPDIF_TX_EN=1

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, DSD
INCLUDE_ONLY_IN_2AMi8o8xxxxxd =
XCC_FLAGS_2AMi8o8xxxxxd = $(BUILD_FLAGS) 		-DDSD_CHANS_DAC=2

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, S/PDIF Tx (8 mixes)
INCLUDE_ONLY_IN_2AMi8o10xxsxxx_mix8 = 
XCC_FLAGS_2AMi8o10xxsxxx_mix8 = $(BUILD_FLAGS)  -DXUA_SPDIF_TX_EN=1 \
												-DMAX_MIX_COUNT=8

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, SPDIF Tx, DSD
INCLUDE_ONLY_IN_2AMi8o10xssxxd =
XCC_FLAGS_2AMi8o10xssxxd = $(BUILD_FLAGS) 		-DXUA_SPDIF_TX_EN=1 \
												-DDSD_CHANS_DAC=2

# Audio Class 2, Async, I2S Master, 16xInput, 10xOutput, ADAT Rx
# Sample rate restriced to 96kHz fit in USB bandwidth
INCLUDE_ONLY_IN_2Ai16o8xxxaxx =
XCC_FLAGS_2Ai16o8xxxaxx = $(BUILD_FLAGS) 		-DXUA_ADAT_RX_EN=1 \
												-DMAX_FREQ=96000

# Audio Class 2, Async, I2S Disabled, 0xInput, 2xOutput, S/PDIF Tx
INCLUDE_ONLY_IN_2AXi0o2xxsxxx = 
XCC_FLAGS_2AXi0o2xxsxxx = $(BUILD_FLAGS) 		-DXUA_SPDIF_TX_EN=1 \
												-DI2S_CHANS_ADC=0 \
												-DI2S_CHANS_DAC=0 \
												-DNUM_USB_CHAN_IN=0 \
												-DNUM_USB_CHAN_OUT=2

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput
INCLUDE_ONLY_IN_2SMi8o8xxxxxx = 
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS)		-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC

