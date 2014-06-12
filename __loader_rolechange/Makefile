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

erase:
	xflash --erase-all --target-file=../app_usb_aud_xk_u8_2c/src/core/xk_usb_audio_u8_2c.xn

flash: 
	xflash  ~/sandboxes/sb_dock_master/sw_audio_dock/app_xuh_aud_dock_xk_u8_2c/bin/xis/app_xuh_aud_dock_xk_u8_2c_xis.xe --loader loader.o --upgrade 1 ../app_usb_aud_xk_u8_2c/bin/2iomx_usba_reboot_mfi/app_usb_aud_xk_u8_2c_2iomx_usba_reboot_mfi.xe --upgrade 2 ../app_usb_aud_xk_u8_2c/bin/2iomx_reboot/app_usb_aud_xk_u8_2c_2iomx_reboot.xe 

clean: 
	rm loader.o 

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

#XMOS_MAKE_PATH ?= ../..
#include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
