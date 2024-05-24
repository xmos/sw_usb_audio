# Configs that have been partially tested, but not as comprehensively as those in the Makefile

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx =

# Audio Class 2, Async, I2S Slave, 8xInput 8xOutput (TDM)
INCLUDE_ONLY_IN_2ASi8o8xxxxxx_tdm8 =
XCC_FLAGS_2ASi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)   -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=96000 \
                                                -DCODEC_MASTER=1 \
                                                -DOUT_VOLUME_IN_MIXER=0

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2ASi8o8xxxxxx = $(BUILD_FLAGS)        -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi8o8xxxxxx =

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx
XCC_FLAGS_2AMi8o10xxsxxx = $(BUILD_FLAGS)       -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2AMi8o10xxsxxx =


# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, DSD
INCLUDE_ONLY_IN_2AMi8o8xxxxxd =
XCC_FLAGS_2AMi8o8xxxxxd = $(BUILD_FLAGS) 		-DDSD_CHANS_DAC=2

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx (8 mixes)
INCLUDE_ONLY_IN_2AMi8o10xxsxxx_mix8 =
XCC_FLAGS_2AMi8o10xxsxxx_mix8 = $(BUILD_FLAGS)  -DXUA_SPDIF_TX_EN=1 \
												-DMAX_MIX_COUNT=8

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, SPDIF Tx, DSD
INCLUDE_ONLY_IN_2AMi8o10xxsxxd =
XCC_FLAGS_2AMi8o10xxsxxd = $(BUILD_FLAGS) 		-DXUA_SPDIF_TX_EN=1 \
												-DDSD_CHANS_DAC=2


# Audio Class 2, Sync, I2S Master, 8xInput, 8xOutput
INCLUDE_ONLY_IN_2SMi8o8xxxxxx =
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS)		-DXUA_SYNCMODE=XUA_SYNCMODE_SYNC

# Audio Class 2, Async, I2S Master, 16xInput, 8xOutput, ADAT Rx
INCLUDE_ONLY_IN_2AMi16o8xxxaxx =
XCC_FLAGS_2AMi16o8xxxaxx = $(BUILD_FLAGS)       -DXUA_ADAT_RX_EN=1

# Audio Class 2, Async, I2S master, 8xInput, 16xOutput, ADAT Tx
INCLUDE_ONLY_IN_2AMi8o16xxxxax =
XCC_FLAGS_2AMi8o16xxxxax = $(BUILD_FLAGS)       -DXUA_ADAT_TX_EN=1

