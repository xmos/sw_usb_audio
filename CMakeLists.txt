cmake_minimum_required(VERSION 3.21)
include($ENV{XMOS_CMAKE_PATH}/xcommon.cmake)
project(sw_usb_audio)

add_subdirectory(app_usb_aud_xk_316_mc)
add_subdirectory(app_usb_aud_xk_216_mc)
add_subdirectory(app_usb_aud_xk_evk_xu316)
add_subdirectory(app_usb_aud_xk_evk_xu316_extrai2s)
