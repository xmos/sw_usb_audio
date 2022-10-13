# Configs that have only had their build process tested

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput, TDM
# (1024x Mclk required for 192/176 TDM)
XCC_FLAGS_2SMi10o10xxxxxx_tdm8 = $(BUILD_FLAGS) -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM \
                                                                                                -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC \
                                                                                                -DMCLK_48=1024*48000 \
                                                                                                -DMCLK_441=1024*44100
INCLUDE_ONLY_IN_2SMi10o10xxxxxx_tdm8 =

