#
# Configs that are partially tested
#

# Enabling "build" test configs implicitly enables "partial" test configs
if(BUILD_TESTED_CONFIGS)
    set(PARTIAL_TESTED_CONFIGS TRUE)
endif()


if(PARTIAL_TESTED_CONFIGS)

# Audio Class 2, Async, I2S Slave, 8xInput, 8xOutput
set(APP_COMPILER_FLAGS_2ASi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DCODEC_MASTER=1)

# Audio Class 2, Async, I2S Master, 32xInput, 32xOutput, TDM
set(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DNUM_USB_CHAN_OUT=32
                                                                  -DI2S_CHANS_DAC=32
                                                                  -DNUM_USB_CHAN_IN=32
                                                                  -DI2S_CHANS_ADC=32
                                                                  -DMAX_FREQ=48000)

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx
set(APP_COMPILER_FLAGS_2AMi8o10xxsxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1)


# Audio Class 2, Async, I2S Slave, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
set(APP_COMPILER_FLAGS_2ASi10o10xssxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                             -DXUA_SPDIF_RX_EN=1
                                                             -DCODEC_MASTER=1)

# Audio Class 2, Async, I2S Master, 10xInput, 8xOutput, S/PDIF Rx
set(APP_COMPILER_FLAGS_2AMi10o8xsxxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_RX_EN=1)

# Audio Class 2, Async, I2S Master, 8xInput, 10xOutput, S/PDIF Tx (8 mixes)
set(APP_COMPILER_FLAGS_2AMi8o10xxsxxx_mix8 ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                                 -DMAX_MIX_COUNT=8)

# Audio Class 2, Async, I2S Master, 16xInput, 8xOutput, ADAT Rx
set(APP_COMPILER_FLAGS_2AMi16o8xxxaxx ${SW_USB_AUDIO_FLAGS}  -DXUA_ADAT_RX_EN=1)

# Audio Class 2, Async, I2S master, 8xInput, 16xOutput, ADAT Tx
set(APP_COMPILER_FLAGS_2AMi8o16xxxxax ${SW_USB_AUDIO_FLAGS}  -DXUA_ADAT_TX_EN=1)

endif()
