# This file provides overrides to the Doxyfile configuration

PROJECT_NAME           = sw_usb_audio
PROJECT_BRIEF          = "USB Audio reference designs"

INPUT                  = ../../lib_xua/lib_xua/api ../../lib_xua/lib_xua/src

PREDEFINED             = C_API= EXTERN_C= UNSAFE= __DOXYGEN__=1 XUA_USB_EN=1
