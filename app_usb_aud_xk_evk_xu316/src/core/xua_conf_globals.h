// Copyright 2025-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include "xk_evk_xu316/board.h"

/* Global to save I2C interface for configuring external audio hardware - used in src/extensions/audiohw.xc */
extern unsafe client interface i2c_master_if i_i2c_client;
