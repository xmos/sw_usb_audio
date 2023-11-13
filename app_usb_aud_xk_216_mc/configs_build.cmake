#
# Configs that have only had their build process tested
#
if(BUILD_TESTED_CONFIGS)

set(APP_COMPILER_FLAGS_1AMi6o2xxxxxx ${SW_USB_AUDIO_FLAGS} -DAUDIO_CLASS=1
                                                           -DNUM_USB_CHAN_IN_FS=6
                                                           -DMAX_FREQ_FS=44100
                                                           -DSTREAM_FORMAT_INPUT_1_RESOLUTION_BITS=16)

set(APP_COMPILER_FLAGS_2AXi0o2xxsxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                           -DI2S_CHANS_ADC=0
                                                           -DI2S_CHANS_DAC=0)

set(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_ADC=32
                                                                  -DI2S_CHANS_DAC=32
                                                                  -DNUM_USB_CHAN_IN=32
                                                                  -DNUM_USB_CHAN_OUT=32
                                                                  -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DMAX_FREQ=48000)

set(APP_COMPILER_FLAGS_2ASi0o8xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_ADC=0
                                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                -DMAX_FREQ=96000
                                                                -DCODEC_MASTER=1)

set(APP_COMPILER_FLAGS_2AMi16o16xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_DAC=16
                                                                  -DI2S_CHANS_ADC=16
                                                                  -DNUM_USB_CHAN_IN=16
                                                                  -DNUM_USB_CHAN_OUT=16
                                                                  -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DMAX_FREQ=96000)

set(APP_COMPILER_FLAGS_2AMi32o32xxsxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_ADC=32
                                                                  -DI2S_CHANS_DAC=32
                                                                  -DNUM_USB_CHAN_IN=32
                                                                  -DNUM_USB_CHAN_OUT=32
                                                                  -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DMAX_FREQ=48000
                                                                  -DXUA_SPDIF_TX_EN=1
                                                                  -DSPDIF_TX_INDEX=0)

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                -DMAX_FREQ=96000)

endif()
