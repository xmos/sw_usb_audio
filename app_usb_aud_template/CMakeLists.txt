cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

set(APP_INCLUDES src src/core src/extensions)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)

set(SW_USB_AUDIO_FLAGS ${EXTRA_BUILD_FLAGS} -O3
                                            -report
                                            -lquadflash
                                            -g
                                            -Wall
                                            -fxscope
                                            -DADAT_TX_USE_SHARED_BUFF=1)

project(app_usb_aud_template)

set(APP_HW_TARGET custom_board.xn)

# Simple 2 in/2 out configuration
set(APP_COMPILER_FLAGS  ${SW_USB_AUDIO_FLAGS}   -DNUM_USB_CHAN_IN=2
                                                -DNUM_USB_CHAN_OUT=2)

XMOS_REGISTER_APP()
