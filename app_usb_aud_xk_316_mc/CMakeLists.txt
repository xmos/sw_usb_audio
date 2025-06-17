cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

set(APP_INCLUDES src src/core src/extensions)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
set(APP_PCA_ENABLE ON)

set(SW_USB_AUDIO_FLAGS ${EXTRA_BUILD_FLAGS} -O3
                                            -report
                                            -lquadflash
                                            -g
                                            -fxscope
                                            -DBOARD_SUPPORT_BOARD=XK_AUDIO_316_MC_AB
                                            -DUSB_TILE=tile[0]
                                            -DADAT_TX_USE_SHARED_BUFF=1
                                            -DXUA_QUAD_SPI_FLASH=1)

## HiBW configs
project(app_usb_aud_xk_316_mc)
set(APP_HW_TARGET xk-audio-316-mc-800.xn) # HiBW configs run at increased clock speed

if(BUILD_TESTED_CONFIGS)
    set(PARTIAL_TESTED_CONFIGS TRUE)
endif()

set(APP_COMPILER_FLAGS_2AMi19o19xxxaax_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=19 -DNUM_USB_CHAN_OUT=19 -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2 -DXUA_ADAT_RX_EN=1 -DXUA_ADAT_TX_EN=1)
set(APP_COMPILER_FLAGS_2AMi20o20xxxaax_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=20 -DNUM_USB_CHAN_OUT=20 -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2 -DXUA_ADAT_RX_EN=1 -DXUA_ADAT_TX_EN=1)

if(PARTIAL_TESTED_CONFIGS)
set(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=30 -DNUM_USB_CHAN_OUT=30 -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2)
set(APP_COMPILER_FLAGS_2AMi30o30xxxaax_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=30 -DNUM_USB_CHAN_OUT=30 -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2 -DXUA_ADAT_RX_EN=1 -DXUA_ADAT_TX_EN=1)

#set(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_usb_loopback_hibw ${SW_USB_AUDIO_FLAGS} -DNUM_USB_CHAN_IN=30 -DNUM_USB_CHAN_OUT=30 -DXUD_USB_ISO_MAX_TXNS_PER_MICROFRAME=2 -DSAMPLE_LOOPBACK=1 -DUAC_FORCE_FEEDBACK_EP=0 -DXUD_NAK_ISO_OUT -DXUD_NAK_ISO_IN -DMAX_FREQ=96000)
endif()
XMOS_REGISTER_APP()

if(PARTIAL_TESTED_CONFIGS)
unset(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_hibw)
unset(APP_COMPILER_FLAGS_2AMi30o30xxxaax_hibw)
endif()
unset(APP_COMPILER_FLAGS_2AMi19o19xxxaax_hibw)
unset(APP_COMPILER_FLAGS_2AMi20o20xxxaax_hibw)
#unset(APP_COMPILER_FLAGS_2AMi30o30xxxxxx_usb_loopback_hibw)


project(app_usb_aud_xk_316_mc)
set(APP_HW_TARGET xk-audio-316-mc.xn)

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS})

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx_mix8 ${SW_USB_AUDIO_FLAGS} -DMAX_MIX_COUNT=8)

set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                -DMAX_FREQ=96000)

set(APP_COMPILER_FLAGS_2ASi8o8xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DCODEC_MASTER=1
                                                                -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                -DMAX_FREQ=96000)

set(APP_COMPILER_FLAGS_2AMi8o8mxxxxx ${SW_USB_AUDIO_FLAGS} -DMIDI=1)

set(APP_COMPILER_FLAGS_2AMi10o10xssxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                             -DXUA_SPDIF_RX_EN=1)

set(APP_COMPILER_FLAGS_2AMi16o16xxxaax ${SW_USB_AUDIO_FLAGS} -DXUA_ADAT_RX_EN=1
                                                             -DXUA_ADAT_TX_EN=1)

set(APP_COMPILER_FLAGS_2AMi18o18mssaax ${SW_USB_AUDIO_FLAGS} -DMIDI=1
                                                             -DXUA_ADAT_RX_EN=1
                                                             -DXUA_ADAT_TX_EN=1
                                                             -DXUA_SPDIF_TX_EN=1
                                                             -DXUA_SPDIF_RX_EN=1
                                                             -DMAX_FREQ=96000)

set(APP_COMPILER_FLAGS_1SMi2o2xxxxxx ${SW_USB_AUDIO_FLAGS} -DAUDIO_CLASS=1
                                                           -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC)

set(APP_COMPILER_FLAGS_2SMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC)

set(APP_COMPILER_FLAGS_2SSi8o8xxxxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SYNCMODE=XUA_SYNCMODE_SYNC
                                                           -DCODEC_MASTER=1)
include(${CMAKE_CURRENT_LIST_DIR}/configs_partial.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/configs_build.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/configs_test.cmake)



XMOS_REGISTER_APP()
