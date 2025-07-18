// Copyright 2022-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef __XC__

#include "i2c.h"
#include <platform.h>
#include <xk_audio_316_mc_ab/board.h>
#include <xscope.h>

extern unsafe client interface i2c_master_if i_i2c_client;
extern void board_setup();
#if HID_CONTROLS > 0
extern void UserHIDPoll();
#endif

#if HID_CONTROLS > 0

    #define USER_MAIN_DECLARATIONS \
        interface i2c_master_if i2c[1];

    #define USER_MAIN_CORES on tile[0]: {\
                                            board_setup();\
                                            xk_audio_316_mc_ab_i2c_master(i2c);\
                                        }\
                            on tile[XUD_TILE]: UserHIDPoll();\
                            on tile[1]: {\
                                            unsafe\
                                            {\
                                                i_i2c_client = i2c[0]; \
                                            }\
                                        }
#else

    #define USER_MAIN_DECLARATIONS \
        chan c_xscope; \
        interface i2c_master_if i2c[1];

    #define USER_MAIN_CORES xscope_host_data(c_xscope); \
                            on tile[0]: {\
                                            board_setup();\
                                            xk_audio_316_mc_ab_i2c_master(i2c);\
                                        }\
                            on tile[1]: {\
                                            xscope_mode_lossy(); \
                                            unsafe\
                                            {\
                                                i_i2c_client = i2c[0]; \
                                            }\
                                        }

#endif
#endif

#endif
