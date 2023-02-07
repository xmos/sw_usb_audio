# Configs that have only had their build process tested

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput, TDM
# (1024x Mclk required for 192/176 TDM)
INCLUDE_ONLY_IN_2SMi10o10xxxxxx_tdm8 =
XCC_FLAGS_2SMi10o10xxxxxx_tdm8 = $(BUILD_FLAGS)           -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                          -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
                                                          -DMCLK_48=1024*48000 \
                                                          -DMCLK_441=1024*44100

# Audio Class 1, Adaptive, I2S Master, 8xInput, 8xOutput, TDM
INCLUDE_ONLY_IN_1DMi8o8xxxxxx =
XCC_FLAGS_1DMi8o8xxxxxx = $(BUILD_FLAGS)                   -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                           -DXUA_SYNCMODE=XUA_SYNCMODE_ADAPT \
                                                           -DAUDIO_CLASS=1

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, Mixer (mixer does volume processing after mix)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_mix8_vol_after = 
XCC_FLAGS_2AMi8o8xxxxxx_mix8_vol_after = $(BUILD_FLAGS)    -DMAX_MIX_COUNT=8 \
                                                           -DOUT_VOLUME_IN_MIXER=1 -DIN_VOLUME_IN_MIXER=1


# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, Mixer (mixer does volume processing before mix)
INCLUDE_ONLY_IN_2AMi8o8xxxxxx_mix8_vol_before = 
XCC_FLAGS_2AMi8o8xxxxxx_mix8_vol_before = $(BUILD_FLAGS)   -DMAX_MIX_COUNT=8 \
                                                           -DOUT_VOLUME_IN_MIXER=1 -DIN_VOLUME_IN_MIXER=1 
                                                           -DOUT_VOLUME_AFTER_MIX=0 -DIN_VOLUME_AFTER_MIX=0
