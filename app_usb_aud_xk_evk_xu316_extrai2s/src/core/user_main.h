// Copyright 2021-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef __XC__

#include <platform.h>
#include "xk_evk_xu316/board.h"

void i2s_driver(chanend c);

extern unsafe chanend uc_i2s;

/* Global to save I2C interface for configuring external audio hardware - used in src/extensions/audiohw.xc */
extern unsafe client interface i2c_master_if i_i2c_client;

/* The I2C master interface connection spans the two tiles: the server runs on tile[0]
 * where the CODEC I2C lines are, the client is used from tile[1]. */
#define USER_MAIN_DECLARATIONS chan c_i2s; interface i2c_master_if i2c[1];

#define USER_MAIN_CORES on tile[1]: {\
                                        par\
                                        {\
                                            i2s_driver(c_i2s);\
                                            unsafe{\
                                                uc_i2s = (chanend) c_i2s;\
                                                i_i2c_client = i2c[0];\
                                            }\
                                        }\
                                    }\
\
                        on tile[0]: {\
                                        xk_evk_xu316_i2c_master(i2c);\
                                    }
#endif

#endif

