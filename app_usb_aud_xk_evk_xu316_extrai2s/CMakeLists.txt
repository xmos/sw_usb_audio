cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(app_usb_aud_xk_evk_xu316_extrai2s)

set(APP_HW_TARGET XK-EVK-XU316)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
set(APP_PCA_ENABLE ON)
set(SW_USB_AUDIO_FLAGS ${EXTRA_BUILD_FLAGS} -fcomment-asm
                                            -Wall
                                            -O3
                                            -report
                                            -lquadflash
                                            -g
                                            -fxscope
                                            -DUSB_TILE=tile[0]
                                            -DADAT_TX_USE_SHARED_BUFF=1
                                            -DXUA_QUAD_SPI_FLASH=1
                                            -DXSCOPE
                                            -DUAC_FORCE_FEEDBACK=1)

set(APP_COMPILER_FLAGS_1AMi2o2xxxxxx ${SW_USB_AUDIO_FLAGS} -DAUDIO_CLASS=1)

set(APP_COMPILER_FLAGS_2AMi2o2xxxxxx ${SW_USB_AUDIO_FLAGS})

set(APP_INCLUDES src src/core src/extensions)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)

XMOS_REGISTER_APP()
