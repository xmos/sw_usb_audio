// Copyright 2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xk_audio_316_mc_ab/board.h>

/* Global to save I2C interface for configuring external audio hardware - used in src/extensions/audiohw.xc */
extern unsafe client interface i2c_master_if i_i2c_client;

extern void board_setup(); // See src/extensions/audiohw.xc

#if HID_CONTROLS > 0
extern void UserHIDPoll(); // See src/extensions/hidbuttons.xc
#endif

/* Note, this declaration could also have made in user_main_declarations.h */
#define USER_MAIN_DECLARATIONS   interface i2c_master_if i2c[1];

