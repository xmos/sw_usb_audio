// Copyright 2025-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

on tile[0]: {
                xk_evk_xu316_i2c_master(i2c);
            }

on tile[1]: {
                unsafe
                {
                    i_i2c_client = i2c[0];
                }
            }
