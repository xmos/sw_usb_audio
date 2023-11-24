cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)

project(app_usb_aud_xk_316_mc_multirate_i2s)

set(APP_HW_TARGET xk-audio-316-mc.xn)

include(${CMAKE_CURRENT_LIST_DIR}/../deps.cmake)

list(APPEND APP_DEPENDENT_MODULES "lib_i2s"
                                  "lib_src")

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
                                            -DQUAD_SPI_FLASH=1
                                            -DXSCOPE
                                            -DUAC_FORCE_FEEDBACK=1
                                            -DMAX_FREQ=192000
                                            -DMIN_FREQ=192000)

# Build config naming scheme:

# Audio Class:          1 or 2
# Sync Mode             A(sync), S(ync) or (a)D(aptive)
# I2S                   M(aster), S(lave) or X (I2S disabled)
# Input                 enabled: i (channelcount)
# Output                enabled: o (channelcount)
# MIDI                  enabled: m, disabled: x
# SPDIF in              enabled: s, disabled: x
# SPDIF out             enabled: s, disabled: x
# ADAT in               enabled: a, disabled: x
# ADAT out              enabled: a, disabled: x
# DSD out               enabled: d, disabled: x
#
# e.g. 2AMi10o10xxsxxx: Audio class 2.0, Asynchronous, I2S Master, input and output enabled (10
# channels each), no MIDI, SPDIF output, no SPDIF input, no ADAT
set(APP_COMPILER_FLAGS_2AMi2o2xxxxxx_asrc ${SW_USB_AUDIO_FLAGS}
                                     -DNUM_USB_CHAN_OUT=2
                                     -DNUM_USB_CHAN_IN=2
                                     -DI2S_CHANS_DAC=2
                                     -DI2S_CHANS_ADC=2
                                     -DUSE_ASRC=1)

set(APP_COMPILER_FLAGS_2AMi2o2xxxxxx_ssrc ${SW_USB_AUDIO_FLAGS}
                                     -DNUM_USB_CHAN_OUT=2
                                     -DNUM_USB_CHAN_IN=2
                                     -DI2S_CHANS_DAC=2
                                     -DI2S_CHANS_ADC=2
                                     -DUSE_ASRC=0)

set(APP_INCLUDES src src/core src/extensions)

set(XMOS_SANDBOX_DIR ${CMAKE_CURRENT_LIST_DIR}/../..)

XMOS_REGISTER_APP()
