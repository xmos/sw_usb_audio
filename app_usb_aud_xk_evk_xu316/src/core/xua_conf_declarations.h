// Copyright 2025-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

/* The I2C master interface connection spans the two tiles: the server runs on tile[0]
 * where the CODEC I2C lines are, the client is used from tile[1]. */
interface i2c_master_if i2c[1];
