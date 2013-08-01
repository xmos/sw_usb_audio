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
	xflash ../app_usb_aud_xk_u8_2c/bin/2ioxs/app_usb_aud_xk_u8_2c_2ioxs.xe --loader loader.o --upgrade 1 ../../sw_audio_dock/app_xuh_audio_dock/bin/xis/app_xuh_audio_dock_xis.xe

flashwithup:
	xflash ../app_usb_aud_xk_u8_2c/bin/2ioxs/app_usb_aud_xk_u8_2c_2ioxs.xe --loader loader.o --upgrade 1 ../app_usb_aud_xk_u8_2c/bin/2ioxs_up1/app_usb_aud_xk_u8_2c_2ioxs_up1.xe --upgrade 2 ../app_usb_aud_xk_u8_2c/bin/2ioxs_up2/app_usb_aud_xk_u8_2c_2ioxs_up2.xe 	

create_upgrades:
	xflash --upgrade 1 ../app_usb_aud_xk_u8_2c/bin/2ioxs_up1/app_usb_aud_xk_u8_2c_2ioxs_up1.xe 0x10000 -o usbaudup1.bin; xflash --upgrade 2 ../app_usb_aud_xk_u8_2c/bin/2ioxs_up2/app_usb_aud_xk_u8_2c_2ioxs_up2.xe 0x10000 -o usbaudup2.bin; tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=usbaudup1_padded.bin; dd if=usbaudup1.bin of=usbaudup1_padded.bin conv=notrunc; cat usbaudup1_padded.bin usbaudup2.bin > usbaudupcat.bin; 

clean: 
	rm loader.o 

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

#XMOS_MAKE_PATH ?= ../..
#include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
