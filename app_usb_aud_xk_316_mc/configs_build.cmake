#
# Configs that have only had their build process tested
#
if(BUILD_TESTED_CONFIGS)

# Audio Class 2, Sync, I2S Master, 10xInput, 10xOutput, TDM
# (1024x Mclk required for 192/176 TDM)
set(APP_COMPILER_FLAGS_2SMi10o10xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC
                                                                  -DMCLK_48=1024*48000
                                                                  -DMCLK_441=1024*44100)

# Audio Class 1, Adaptive, I2S Master, 8xInput, 8xOutput, TDM
set(APP_COMPILER_FLAGS_1DMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                           -DXUA_SYNCMODE=XUA_SYNCMODE_ADAPT
                                                           -DAUDIO_CLASS=1)

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, Mixer (mixer does volume processing after mix)
set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx_mix8_vol_after ${SW_USB_AUDIO_FLAGS} -DMAX_MIX_COUNT=8
                                                                          -DOUT_VOLUME_IN_MIXER=1
                                                                          -DIN_VOLUME_IN_MIXER=1)


# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, Mixer (mixer does volume processing before mix)
set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx_mix8_vol_before ${SW_USB_AUDIO_FLAGS} -DMAX_MIX_COUNT=8
                                                                           -DOUT_VOLUME_IN_MIXER=1
                                                                           -DIN_VOLUME_IN_MIXER=1
                                                                           -DOUT_VOLUME_AFTER_MIX=0
                                                                           -DIN_VOLUME_AFTER_MIX=0)

# Audio Class 2, Async, I2S Master, 0xInput, 0xOutput, HID enabled
set(APP_COMPILER_FLAGS_2AMi0o0xxxxxx_hid ${SW_USB_AUDIO_FLAGS} -DHID_CONTROLS=1 -DNUM_USB_CHAN_OUT=0 -DNUM_USB_CHAN_IN=0)

# Audio Class 2, Async, I2S Master, 0xInput, 8xOutput, HID enabled
set(APP_COMPILER_FLAGS_2AMi0o8xxxxxx_hid ${SW_USB_AUDIO_FLAGS} -DHID_CONTROLS=1 -DNUM_USB_CHAN_IN=0)

endif()
