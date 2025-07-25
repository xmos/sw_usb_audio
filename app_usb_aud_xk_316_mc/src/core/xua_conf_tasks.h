// Copyright 2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#if HID_CONTROLS > 0
on tile[XUD_TILE]: UserHIDPoll();
#endif

on tile[0]: {
                board_setup();
                xk_audio_316_mc_ab_i2c_master(i2c);
            }


on tile[1]: {
                unsafe
                {
                    i_i2c_client = i2c[0];
                }
            }

