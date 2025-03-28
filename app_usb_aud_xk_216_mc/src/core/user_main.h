// Copyright 2022-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#ifndef USER_MAIN_H
#define USER_MAIN_H

#ifdef __XC__

#include <platform.h>
#if HID_CONTROLS > 0
void UserHIDPoll();

#define USER_MAIN_CORES on tile[XUD_TILE]: {\
                                        UserHIDPoll();\
                                    }
#endif  // HID_CONTROLS > 0

#endif

#endif
