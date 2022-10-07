# Configs that have been partially tested, but not as comprehensively as those in the Makefile

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, TDM
XCC_FLAGS_2AMi8o8xxxxxx_tdm8  = $(BUILD_FLAGS) -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                               -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_tdm8 =


# Audio Class 2, Async, I2S Slave, 0xInput, 8xOutput, TDM
XCC_FLAGS_2ASi0o8xxxxxx_tdm8 = $(BUILD_FLAGS) -DI2S_CHANS_ADC=0 \
                                              -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                              -DMAX_FREQ=96000 \
                                              -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi0o8xxxxxx_tdm8 =


# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, TDM
# Note: sample rate restricted to 96K to fit in USB bandwidth
XCC_FLAGS_2AMi16o16xxxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=16 \
                                                 -DI2S_CHANS_ADC=16 \
                                                 -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                 -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2AMi16o16xxxxxx_tdm8 =

# Audio Class 2, Async, I2S Master, 32xInput, 32xOutput, TDM
XCC_FLAGS_2AMi32o32xxxxxx_tdm8  = $(BUILD_FLAGS) -DI2S_CHANS_DAC=32 \
                                                -DI2S_CHANS_ADC=32 \
                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=48000
INCLUDE_ONLY_IN_2AMi32o32xxxxxx_tdm8 =

# Audio Class 2, Async, I2S Master, 32xInput, 32xOutput, S/PDIF Tx, TDM
XCC_FLAGS_2AMi32o32xxsxxx_tdm8 = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 \
                                                -DI2S_CHANS_ADC=32 \
                                                -DI2S_CHANS_DAC=32 \
                                                -DNUM_USB_CHAN_OUT=32 \
                                                -DNUM_USB_CHAN_IN=32 \
                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=48000
INCLUDE_ONLY_IN_2AMi32o32xxsxxx_tdm8 =

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, MIDI, S/PDIF Tx
XCC_FLAGS_2AMi10o10mxsxxx = $(BUILD_FLAGS) -DMIDI=1 \
                                           -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2AMi10o10mxsxxx =

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, DSD
XCC_FLAGS_2AMi8o8xxxxxd = $(BUILD_FLAGS) -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2AMi8o8xxxxxd =

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
XCC_FLAGS_2AMi8o8xxxxxx = $(BUILD_FLAGS)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx =

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
XCC_FLAGS_2ASi8o8xxxxxx = $(BUILD_FLAGS) -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi8o8xxxxxx =

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx
XCC_FLAGS_2AMi8o10xxsxxx = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1
INCLUDE_ONLY_IN_2AMi8o10xxsxxx =

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx, 8 mixes
XCC_FLAGS_2AMi8o10xxsxxx_mix8 = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 \
                                               -DMAX_MIX_COUNT=8
INCLUDE_ONLY_IN_2AMi8o10xxsxxx_mix8 =

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx, DSD
XCC_FLAGS_2AMi8o10xxsxxd = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 \
                                          -DDSD_CHANS_DAC=2
INCLUDE_ONLY_IN_2AMi8o10xxsxxd =

# Audio Class 2, Async, I2S Master, 8xInput, 16xOutput, ADAT Tx
XCC_FLAGS_2AMi8o16xxxxax = $(BUILD_FLAGS) -DXUA_ADAT_TX_EN=1 \
                                          -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2AMi8o16xxxxax =

# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, ADAT Rx, ADAT Tx
# Sample rate restriced to 96kHz fit in USB bandwidth
XCC_FLAGS_2AMi16o16xxxaax = $(BUILD_FLAGS) -DXUA_ADAT_RX_EN=1 \
                                           -DXUA_ADAT_TX_EN=1 \
                                           -DMAX_FREQ=96000
INCLUDE_ONLY_IN_2AMi16o16xxxaax =

# Audio Class 1, Async, I2S Master, 8xInput, 2xOutput
XCC_FLAGS_1AMi8o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 \
                                         -DNUM_USB_CHAN_IN_FS=6 \
                                         -DMAX_FREQ_FS=44100 \
                                         -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16
INCLUDE_ONLY_IN_1AMi8o2xxxxxx =

# Audio Class 2, Async, I2S Master, No I2s Input, No I2S Output, S/PDIF Tx
XCC_FLAGS_2AMi0o2xxsxxx_noi2s = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 \
                                               -DI2S_CHANS_ADC=0 \
                                               -DI2S_CHANS_DAC=0
INCLUDE_ONLY_IN_2AMi0o2xxsxxx_noi2s =

# Audio Class 2, Sync, 8xInput, 8xOutput
XCC_FLAGS_2SMi8o8xxxxxx = $(BUILD_FLAGS) -DXUA_SYNCMODE=3
INCLUDE_ONLY_IN_2SMi8o8xxxxxx =

