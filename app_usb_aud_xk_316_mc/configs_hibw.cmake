#
# High bandwidth ISO endpoint configurations.
#

project(app_usb_aud_xk_316_mc)
set(APP_HW_TARGET xk-audio-316-mc-800.xn) # HiBW configs run at increased clock speed

if(BUILD_TESTED_CONFIGS)
    set(PARTIAL_TESTED_CONFIGS TRUE)
endif()

set(APP_COMPILER_FLAGS_2AMi20o20xxxaax_hibw ${SW_USB_AUDIO_FLAGS}   -DNUM_USB_CHAN_IN=20
                                                                    -DNUM_USB_CHAN_OUT=20
                                                                    -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                    -DXUA_ADAT_RX_EN=1
                                                                    -DXUA_ADAT_TX_EN=1)

set(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8_mix8_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=32
                                                                            -DNUM_USB_CHAN_OUT=32
                                                                            -DI2S_CHANS_ADC=32
                                                                            -DI2S_CHANS_DAC=32
                                                                            -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                            -DMAX_FREQ=96000
                                                                            -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                            -DMAX_MIX_COUNT=8)

if(PARTIAL_TESTED_CONFIGS)
set(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_hibw ${SW_USB_AUDIO_FLAGS}   -DNUM_USB_CHAN_IN=30
                                                                    -DNUM_USB_CHAN_OUT=30
                                                                    -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                    -DMAX_FREQ=96000)

set(APP_COMPILER_FLAGS_2AMi30o30xxxaax_hibw ${SW_USB_AUDIO_FLAGS}   -DNUM_USB_CHAN_IN=30
                                                                    -DNUM_USB_CHAN_OUT=30
                                                                    -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                    -DMAX_FREQ=96000
                                                                    -DXUA_ADAT_RX_EN=1
                                                                    -DXUA_ADAT_TX_EN=1)

set(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8_hibw ${SW_USB_AUDIO_FLAGS}          -DNUM_USB_CHAN_IN=32
                                                                                -DNUM_USB_CHAN_OUT=32
                                                                                -DI2S_CHANS_ADC=32
                                                                                -DI2S_CHANS_DAC=32
                                                                                -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                                -DMAX_FREQ=96000
                                                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM)
endif()

if(BUILD_TESTED_CONFIGS)
set(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_usblb_hibw ${SW_USB_AUDIO_FLAGS}     -DNUM_USB_CHAN_IN=30
                                                                            -DNUM_USB_CHAN_OUT=30
                                                                            -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2
                                                                            -DUSB_LOOPBACK=1
                                                                            -DUAC_FORCE_FEEDBACK_EP=0
                                                                            -DXUD_NAK_ISO_OUT
                                                                            -D_XUD_NAK_ISO_IN
                                                                            -DMAX_FREQ=96000)
endif()

XMOS_REGISTER_APP()

if(PARTIAL_TESTED_CONFIGS)
unset(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_hibw)
unset(APP_COMPILER_FLAGS_2AMi30o30xxxaax_hibw)
unset(APP_COMPILER_FLAGS_2AMi24o24xxxxxx_tdm8_mix8_hibw)
unset(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8_hibw)
endif()
if(BUILD_TESTED_CONFIGS)
unset(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_usblb_hibw)
endif()
unset(APP_COMPILER_FLAGS_2AMi20o20xxxaax_hibw)
unset(APP_COMPILER_FLAGS_2AMi32o32xxxxxx_tdm8_mix8_hibw)
