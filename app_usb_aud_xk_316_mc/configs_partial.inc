# Configs that have been partially tested, but not as comprehensively as those in the Makefile

#
# Asynchronous Mode Configs
#
# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
INCLUDE_ONLY_IN_2AMi8o8xxxxxx =
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2ASi8o8xxxxxx = $(BUILD_FLAGS)		-DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi8o8xxxxxx =

# Audio Class 2, Async, I2S Master, 32xInput, 32xOutput, TDM
INCLUDE_ONLY_IN_2AMi32o32xxxxxx_tdm8 =
XCC_FLAGS_2AMi32o32xxxxxx_tdm8 = $(BUILD_FLAGS)	-DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
												-DNUM_USB_CHAN_OUT=32 \
												-DI2S_CHANS_DAC=32 \
												-DNUM_USB_CHAN_IN=32 \
												-DI2S_CHANS_ADC=32 \
												-DMAX_FREQ=48000

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx
INCLUDE_ONLY_IN_2AMi8o10xxsxxx =
XCC_FLAGS_2AMi8o10xxsxxx = $(BUILD_FLAGS)		-DXUA_SPDIF_TX_EN=1

# Audio Class 2, Async, I2S Slave, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
INCLUDE_ONLY_IN_2ASi10o10xssxxx =
XCC_FLAGS_2ASi10o10xssxxx = $(BUILD_FLAGS)		-DXUA_SPDIF_TX_EN=1 \
						   						-DXUA_SPDIF_RX_EN=1 \
												-DCODEC_MASTER=1

# Audio Class 2, Async, I2S Master, 10xInput, 8xOutput, S/PDIF Rx
INCLUDE_ONLY_IN_2AMi10o8xsxxxx =
XCC_FLAGS_2AMi10o8xsxxxx = $(BUILD_FLAGS) 		-DXUA_SPDIF_RX_EN=1


# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx (8 mixes)
INCLUDE_ONLY_IN_2AMi8o10xxsxxx_mix8 =
XCC_FLAGS_2AMi8o10xxsxxx_mix8 = $(BUILD_FLAGS)  -DXUA_SPDIF_TX_EN=1 \
                                                -DMAX_MIX_COUNT=8

# Audio Class 2, Async, I2S Master, 16xInput, 8xOutput, ADAT Rx
INCLUDE_ONLY_IN_2AMi16o8xxxaxx =
XCC_FLAGS_2AMi16o8xxxaxx = $(BUILD_FLAGS)       -DXUA_ADAT_RX_EN=1

# Audio Class 2, Async, I2S master, 8xInput, 16xOutput, ADAT Tx
INCLUDE_ONLY_IN_2AMi8o16xxxxax =
XCC_FLAGS_2AMi8o16xxxxax = $(BUILD_FLAGS)       -DXUA_ADAT_TX_EN=1

