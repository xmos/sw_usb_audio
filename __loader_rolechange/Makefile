# The TARGET variable determines what target system the application is 
# compiled for. It either refers to an XN file in the source directories
# or a valid argument for the --target option when compiling.

TARGET = xk_usb_audio_u8_2c.xn
APP_NAME =

# The flags passed to xcc when building the application
BUILD_FLAGS     = -Wall -O3 -report -lflash -g

XCC_FLAGS = $(BUILD_FLAGS)

XE_USB_AUDIO 	 = ../app_usb_aud_xk_u8_2c/bin/2iomx_reboot/app_usb_aud_xk_u8_2c_2iomx_reboot.xe
XE_DOCK			 = ~/sandboxes/sb_dock_master/sw_audio_dock/app_xuh_aud_dock_xk_u8_2c/bin/xix_reboot/app_xuh_aud_dock_xk_u8_2c_xix_reboot.xe
XE_USB_AUDIO_MFI = ../app_usb_aud_xk_u8_2c/bin/2iomx_usba_reboot_mfi/app_usb_aud_xk_u8_2c_2iomx_usba_reboot_mfi.xe

XE_USB_AUDIO_upgrade1 		= ../app_usb_aud_xk_u8_2c/bin/2iomx_reboot_upgrade1/app_usb_aud_xk_u8_2c_2iomx_reboot_upgrade1.xe
XE_DOCK_upgrade1		  	= ~/sandboxes/sb_dock_master/sw_audio_dock/app_xuh_aud_dock_xk_u8_2c/bin/xix_reboot_upgrade1/app_xuh_aud_dock_xk_u8_2c_xix_reboot_upgrade1.xe
XE_USB_AUDIO_MFI_upgrade1 	= ../app_usb_aud_xk_u8_2c/bin/2iomx_usba_reboot_mfi_upgrade1/app_usb_aud_xk_u8_2c_2iomx_usba_reboot_mfi_upgrade1.xe

XE_USB_AUDIO_upgrade2 		= ../app_usb_aud_xk_u8_2c/bin/2iomx_reboot_upgrade2/app_usb_aud_xk_u8_2c_2iomx_reboot_upgrade2.xe
XE_DOCK_upgrade2		  	= ~/sandboxes/sb_dock_master/sw_audio_dock/app_xuh_aud_dock_xk_u8_2c/bin/xix_reboot_upgrade2/app_xuh_aud_dock_xk_u8_2c_xix_reboot_upgrade2.xe
XE_USB_AUDIO_MFI_upgrade2 	= ../app_usb_aud_xk_u8_2c/bin/2iomx_usba_reboot_mfi_upgrade2/app_usb_aud_xk_u8_2c_2iomx_usba_reboot_mfi_upgrade2.xe


all:
	xcc $(XCC_FLAGS) -c loader.xc -o loader.o

erase:
	xflash --erase-all --target-file=../app_usb_aud_xk_u8_2c/src/core/xk_usb_audio_u8_2c.xn

flash: 
	xflash  $(XE_USB_AUDIO) --loader loader.o --upgrade 1 $(XE_DOCK) --upgrade 2 $(XE_USB_AUDIO_MFI) 

create_upgrades:
	xflash --factory-version 13 --upgrade 1 $(XE_DOCK) -o upgrade_dock.bin; 
	xflash --factory-version 13 --upgrade 2 $(XE_USB_AUDIO_MFI) -o upgrade_usb_mfi.bin;
	xflash --factory-version 13 --upgrade 3 $(XE_USB_AUDIO) -o upgrade_usb.bin;
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_dock_padded.bin; 
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_usb_mfi_padded.bin; 
	dd if=upgrade_usb.bin of=upgrade_dock_padded.bin conv=notrunc; 
	dd if=upgrade_dock.bin of=upgrade_usb_mfi_padded.bin conv=notrunc; 
	cat upgrade_dock_padded.bin upgrade_usb_mfi_padded.bin upgrade_usb.bin> upgrade_final.bin; 

create_upgrades1:
	xflash --factory-version 13 --upgrade 1 $(XE_DOCK_upgrade1) -o upgrade_dock.bin; 
	xflash --factory-version 13 --upgrade 2 $(XE_USB_AUDIO_MFI_upgrade1) -o upgrade_usb_mfi.bin;
	xflash --factory-version 13 --upgrade 3 $(XE_USB_AUDIO_upgrade1) -o upgrade_usb.bin;
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_dock_padded.bin; 
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_usb_mfi_padded.bin; 
	dd if=upgrade_usb.bin of=upgrade_dock_padded.bin conv=notrunc; 
	dd if=upgrade_dock.bin of=upgrade_usb_mfi_padded.bin conv=notrunc; 
	cat upgrade_dock_padded.bin upgrade_usb_mfi_padded.bin upgrade_usb.bin> upgrade_final1.bin; 

create_upgrades2:
	xflash --factory-version 13 --upgrade 1 $(XE_DOCK_upgrade2) -o upgrade_dock.bin; 
	xflash --factory-version 13 --upgrade 2 $(XE_USB_AUDIO_MFI_upgrade2) -o upgrade_usb_mfi.bin;
	xflash --factory-version 13 --upgrade 3 $(XE_USB_AUDIO_upgrade2) -o upgrade_usb.bin;
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_dock_padded.bin; 
	tr "\000" "\000" < /dev/zero | dd ibs=1k count=64 of=upgrade_usb_mfi_padded.bin; 
	dd if=upgrade_usb.bin of=upgrade_dock_padded.bin conv=notrunc; 
	dd if=upgrade_dock.bin of=upgrade_usb_mfi_padded.bin conv=notrunc; 
	cat upgrade_dock_padded.bin upgrade_usb_mfi_padded.bin upgrade_usb.bin> upgrade_final2.bin; 

clean: 
	rm loader.o *.bin

#=============================================================================
# The following part of the Makefile includes the common build infrastructure
# for compiling XMOS applications. You should not need to edit below here.

#XMOS_MAKE_PATH ?= ../..
#include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
