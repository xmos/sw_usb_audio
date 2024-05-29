cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_usb_aud_xk_216_mc)

set(APP_HW_TARGET xk-audio-216-mc.xn)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
set(APP_PCA_ENABLE ON)
set(SW_USB_AUDIO_FLAGS ${EXTRA_BUILD_FLAGS} -O3
                                            -report
                                            -lquadflash
                                            -g
                                            -fxscope
                                            -DUSB_TILE=tile[1]
                                            -DADAT_TX_USE_SHARED_BUFF=1
                                            -DXUA_QUAD_SPI_FLASH=1)

set(APP_COMPILER_FLAGS_1AMi2o2xxxxxx ${SW_USB_AUDIO_FLAGS} -DAUDIO_CLASS=1)

set(APP_COMPILER_FLAGS_2AMi10o10xssxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                             -DXUA_SPDIF_RX_EN=1)

set(APP_COMPILER_FLAGS_2ASi10o10xssxxx ${SW_USB_AUDIO_FLAGS} -DXUA_SPDIF_TX_EN=1
                                                             -DXUA_SPDIF_RX_EN=1
                                                             -DCODEC_MASTER=1)

set(APP_COMPILER_FLAGS_2AMi8o10mxsxxx ${SW_USB_AUDIO_FLAGS} -DMIDI=1
                                                            -DXUA_SPDIF_TX_EN=1)

set(APP_COMPILER_FLAGS_2ASi16o16xxxxxx_tdm8 ${SW_USB_AUDIO_FLAGS} -DI2S_CHANS_ADC=16
                                                                  -DI2S_CHANS_DAC=16
                                                                  -DNUM_USB_CHAN_IN=16
                                                                  -DNUM_USB_CHAN_OUT=16
                                                                  -DXUA_PCM_FORMAT=XUA_PCM_FORMAT_TDM
                                                                  -DMAX_FREQ=96000
                                                                  -DCODEC_MASTER=1
                                                                  -DOUT_VOLUME_IN_MIXER=0)

set(APP_COMPILER_FLAGS_2AMi16o16xxxaax ${SW_USB_AUDIO_FLAGS} -DXUA_ADAT_RX_EN=1 -DXUA_ADAT_TX_EN=1)

set(APP_COMPILER_FLAGS_2AMi18o18mssaax ${SW_USB_AUDIO_FLAGS} -DMIDI=1 -DXUA_ADAT_RX_EN=1 -DXUA_ADAT_TX_EN=1 -DXUA_SPDIF_TX_EN=1 -DXUA_SPDIF_RX_EN=1 -DMAX_FREQ=96000)

include(${CMAKE_CURRENT_LIST_DIR}/configs_partial.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/configs_build.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/configs_test.cmake)

set(APP_INCLUDES src src/core src/extensions)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)

XMOS_REGISTER_APP()
