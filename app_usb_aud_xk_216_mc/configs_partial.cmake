#
# Configs that have been partially tested.
#

# Enabling "build" test configs implicitly enables "partial" test configs
if(BUILD_TESTED_CONFIGS)
    set(PARTIAL_TESTED_CONFIGS TRUE)
endif()


if(PARTIAL_TESTED_CONFIGS)

set(APP_COMPILER_FLAGS_1AMi2o2xxxxxx ${SW_USB_AUDIO_FLAGS} -DAUDIO_CLASS=1)

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS})

set(APP_COMPILER_FLAGS_2ASi8o8xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                -DMAX_FREQ=96000 -DCODEC_MASTER=1
                                                                -DOUT_VOLUME_IN_MIXER=0)

set(APP_COMPILER_FLAGS_2ASi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DCODEC_MASTER=1)

set(APP_COMPILER_FLAGS_2AMi8o10xxsxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1)

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxd ${SW_USB_AUDIO_FLAGS} -DDSD_CHANS_DAC=2)

set(APP_COMPILER_FLAGS_2AMi8o10xxsxxx_mix8 ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                                 -DMAX_MIX_COUNT=8)

set(APP_COMPILER_FLAGS_2AMi8o10xxsxxd ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                            -DDSD_CHANS_DAC=2)


set(APP_COMPILER_FLAGS_2SMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC)

set(APP_COMPILER_FLAGS_2AMi16o8xxxaxx ${SW_USB_AUDIO_FLAGS} -DXUA_ADAT_RX_EN=1)

set(APP_COMPILER_FLAGS_2AMi8o16xxxxax ${SW_USB_AUDIO_FLAGS} -DXUA_ADAT_TX_EN=1)

# Note, TDM requires more MIPs than I2S so we do volume processin in the decouple task
set(APP_COMPILER_FLAGS_2ASi16o16xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_ADC=16
                                                                  -DI2S_CHANS_DAC=16
                                                                  -DNUM_USB_CHAN_IN=16
                                                                  -DNUM_USB_CHAN_OUT=16
                                                                  -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DMAX_FREQ=96000
                                                                  -DCODEC_MASTER=1
                                                                  -DOUT_VOLUME_IN_MIXER=0)

endif()
