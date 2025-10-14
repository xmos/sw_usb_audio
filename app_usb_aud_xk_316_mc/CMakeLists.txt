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
                                            -Wall
                                            -fxscope
                                            -DBOARD_SUPPORT_BOARD=XK_AUDIO_316_MC_AB
                                            -DADAT_TX_USE_SHARED_BUFF=1)

#
# HiBW configs
#
include(${CMAKE_CURRENT_LIST_DIR}/configs_hibw.cmake)

project(app_usb_aud_xk_316_mc)
set(APP_HW_TARGET xk-audio-316-mc.xn)


# Build config naming scheme:
#
# Audio Class:   1 or 2
# Sync Mode      A(sync) or S(ync)
# I2S            M(aster) or S(lave)
# Input          enabled: i (channelcount)
# Output         enabled: o (channelcount)
# MIDI           enabled: m, disabled: x
# SPDIF in       enabled: s, disabled: x
# SPDIF out      enabled: s, disabled: x
# ADAT in        enabled: a, disabled: x
# ADAT out       enabled: a, disabled: x
# DSD out        enabled: d, disabled: x
#
# e.g. 2AMi10o10xxsxxx: Audio class 2.0, Asynchronous, I2S Master, input and output enabled (10 channels each), no MIDI, SPDIF output, no SPDIF input, no ADAT
#
# Additional tags may be added to the end of the build config name to indicate special features or configurations.

#
# Tested build configs
#

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput
set(APP_COMPILER_FLAGS_2AMi8o8xxxxxx ${SW_USB_AUDIO_FLAGS})

# Audio Class 2, Async, I2S Master, 10xInput, 10xOutput, S/PDIF Tx, S/PDIF Rx
set(APP_COMPILER_FLAGS_2AMi10o10xssxxx ${SW_USB_AUDIO_FLAGS}   -DXUA_SPDIF_TX_EN=1
                                                               -DXUA_SPDIF_RX_EN=1)
# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, ADAT Tx, ADAT Rx
set(APP_COMPILER_FLAGS_2AMi16o16xxxaax ${SW_USB_AUDIO_FLAGS}   -DXUA_ADAT_RX_EN=1
                                                               -DXUA_ADAT_TX_EN=1)

# Audio Class 2, Async, I2S Master, 16xInput, 16xOutput, ADAT Tx, ADAT Rx
# Note, limited to 96kHz sample rate
set(APP_COMPILER_FLAGS_2AMi18o18mssaax ${SW_USB_AUDIO_FLAGS}   -DMIDI=1
                                                               -DXUA_ADAT_RX_EN=1
                                                               -DXUA_ADAT_TX_EN=1
                                                               -DXUA_SPDIF_TX_EN=1
                                                               -DXUA_SPDIF_RX_EN=1
                                                               -DMAX_FREQ=96000)

#
# Partially-tested build configs
#
include(${CMAKE_CURRENT_LIST_DIR}/configs_partial.cmake)

#
# Build (only) tested build configs
#
include(${CMAKE_CURRENT_LIST_DIR}/configs_build.cmake)

#
# Build configs used only for testing purpses
#
include(${CMAKE_CURRENT_LIST_DIR}/configs_test.cmake)

XMOS_REGISTER_APP()
