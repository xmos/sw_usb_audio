// Copyright 2015-2024 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#include "app_usb_aud_xk_216_mc.h"

#if USB_SEL_A

#include <interrupt.h>

register_interrupt_handler(HandleRebootTimeout, 1, 200)

#endif
