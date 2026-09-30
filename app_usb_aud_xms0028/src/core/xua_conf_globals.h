// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xms0028/board.h>

extern unsafe client interface i2c_master_if i_i2c_client;

#define USER_MAIN_DECLARATIONS interface i2c_master_if i2c[1];
