# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk_usb_audio_u8_2c.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -Wall -O3 -report -lflash -g

XCC_FLAGS = $(BUILD_FLAGS)

all:
	xcc $(XCC_FLAGS) -c loader.xc -o loader.o

flash:
	xflash ../app_usb_aud_xk_u8_2c/bin/2ioxs/app_usb_aud_xk_u8_2c_2ioxs.xe --loader loader.o --upgrade 1 ~/sb_idock_mfa/sw_audio_dock/app_xuh_audio_dock/bin/app_xuh_audio_dock.xe 

clean: 
	rm loader.o

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

#XMOS_MAKE_PATH ?= ../..
#include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
