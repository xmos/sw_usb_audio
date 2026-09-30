cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

set(APP_INCLUDES src src/core src/extensions)
set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)
include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)
# XMS0028 board support is pending merge into lib_board_support develop.
set(APP_DEPENDENT_MODULES "lib_xua(develop)"
                          "lib_i2c(6.4.1)"
                          "lib_i2s(6.0.1)"
                          "lib_board_support(experimental/xms0028)")

set(SW_USB_AUDIO_FLAGS ${EXTRA_BUILD_FLAGS} -O3
                                             -report
                                             -lquadflash
                                             -g
                                              -Wall
                                              -fxscope
                                              -DBOARD_SUPPORT_BOARD=XMS0028
                                              -DADAT_TX_USE_SHARED_BUFF=1)

project(app_usb_aud_xms0028)

set(APP_HW_TARGET xms0028.xn)

set(APP_COMPILER_FLAGS ${SW_USB_AUDIO_FLAGS}
                       -DNUM_USB_CHAN_IN=2
                       -DNUM_USB_CHAN_OUT=2
                       -DXUA_I2S_N_BITS=32)

XMOS_REGISTER_APP()
