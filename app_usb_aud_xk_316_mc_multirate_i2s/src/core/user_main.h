
#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef __XC__

#include "i2c.h"
#include <print.h>
#include <xs1.h>
#include <platform.h>

void i2s_driver(chanend c);
extern unsafe chanend uc_i2s;

extern unsafe client interface i2c_master_if i_i2c_client;
extern void interface_saver(client interface i2c_master_if i);
extern void board_setup();

/* I2C interface ports */
extern port p_scl;
extern port p_sda;

#define USER_MAIN_DECLARATIONS \
    chan c_i2s; chan c_audiohw;\
    interface i2c_master_if i2c[1];

#define USER_MAIN_CORES on tile[0]: {\
                                        board_setup();\
                                        i2c_master(i2c, 1, p_scl, p_sda, 100);\
                                    }\
\
                        on tile[1]: {\
                                        par\
                                        {\
                                            i2s_driver(c_i2s);\
                                            unsafe\
                                            {\
                                                uc_i2s = (chanend) c_i2s;\
                                                i_i2c_client = i2c[0];\
                                            }\
                                        }\
                                    }
#endif
#endif


