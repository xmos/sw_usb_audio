# Configs that have only had their build process tested

# Audio Class 1, Async, I2S Master, 8xInput, 2xOutput
XCC_FLAGS_1AMi6o2xxxxxx = $(BUILD_FLAGS) -DAUDIO_CLASS=1 \
                                         -DNUM_USB_CHAN_IN_FS=6 \
                                         -DMAX_FREQ_FS=44100 \
                                         -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16
INCLUDE_ONLY_IN_1AMi6o2xxxxxx =

# Audio Class 2, Async, I2S Master, No I2s Input, No I2S Output, S/PDIF Tx
XCC_FLAGS_2AXi0o2xxsxxx = $(BUILD_FLAGS) -DXUA_SPDIF_TX_EN=1 \
                                         -DI2S_CHANS_ADC=0 \
                                         -DI2S_CHANS_DAC=0
INCLUDE_ONLY_IN_2AXi0o2xxsxxx =

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

# Audio Class 2, Async, I2S Master, 32xInput 32xOutput (TDM)
INCLUDE_ONLY_IN_2AMi32o32xxxxxx_tdm8 =
XCC_FLAGS_2AMi32o32xxxxxx_tdm8 = $(BUILD_FLAGS) -DI2S_CHANS_ADC=32 \
                                                -DI2S_CHANS_DAC=32 \
                                                -DNUM_USB_CHAN_IN=32 \
                                                -DNUM_USB_CHAN_OUT=32 \
                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                -DMAX_FREQ=48000

# Audio Class 2, Async, I2S Slave, 0xInput, 8xOutput, TDM
XCC_FLAGS_2ASi0o8xxxxxx_tdm8 = $(BUILD_FLAGS) -DI2S_CHANS_ADC=0 \
                                              -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                              -DMAX_FREQ=96000 \
                                              -DCODEC_MASTER=1
INCLUDE_ONLY_IN_2ASi0o8xxxxxx_tdm8 =

# Audio Class 2, Async, I2S Master, 16xInput 16xOutput (TDM)
INCLUDE_ONLY_IN_2AMi16o16xxxxxx_tdm8 =
XCC_FLAGS_2AMi16o16xxxxxx_tdm8 = $(BUILD_FLAGS) -DI2S_CHANS_ADC=16 \
                                                                                                -DI2S_CHANS_DAC=16 \
                                                                                                -DNUM_USB_CHAN_IN=16 \
                                                                                                -DNUM_USB_CHAN_OUT=16 \
                                                                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                                                                -DMAX_FREQ=96000

# Audio Class 2, Async, I2S Master, 32xInput 32xOutput, S/PDIF Tx (TDM)
INCLUDE_ONLY_IN_2AMi32o32xxsxxx_tdm8 =
XCC_FLAGS_2AMi32o32xxsxxx_tdm8 = $(BUILD_FLAGS) -DI2S_CHANS_ADC=32 \
                                                                                                -DI2S_CHANS_DAC=32 \
                                                                                                -DNUM_USB_CHAN_IN=32 \
                                                                                                -DNUM_USB_CHAN_OUT=32 \
                                                                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                                                                -DMAX_FREQ=48000 \
                                                                                                -DXUA_SPDIF_TX_EN=1 \
                                                                                                -DSPDIF_TX_INDEX=0

# Audio Class 2, Async, I2S Master, 8xInput 8xOutput (TDM)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_tdm8 =
XCC_FLAGS_2AMi8o8xxxxxx_tdm8 = $(BUILD_FLAGS)   -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                                                                -DMAX_FREQ=96000
