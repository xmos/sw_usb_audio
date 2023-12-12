cmake_minimum_required(VERSION 3.5)
project(volcontrol)

if(NOT CMAKE_SYSTEM_NAME MATCHES Darwin)
    message(FATAL_ERROR "CMake build of volcontrol is only supported on MacOS")
endif()

add_executable(volcontrol volcontrol.cpp macos/volcontrol_impl.cpp)
target_include_directories(volcontrol PRIVATE ${CMAKE_CURRENT_LIST_DIR}
                                              macos)
target_compile_options(volcontrol PRIVATE -Wall -Wextra)
target_link_libraries(volcontrol PRIVATE "-framework AudioToolbox"
                                         "-framework CoreAudio"
                                         "-framework CoreFoundation")
