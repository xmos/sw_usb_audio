#ifndef USER_MAIN_H
#define USER_MAIN_H

#ifdef __XC__

#include "i2c.h"
#include <print.h>
#include <xs1.h>
#include <platform.h>

/*
*    TODO: this wrapper is required rather than simply the following to avoid compiler error (bugzilla #18671) 
*    
*    extern unsafe client interface i2c_master i_i2c_client;
*
*    ...
*
*    {
*        i_i2c_client = i2c[0];
*    }
*
*
*   Note, must declare elsewhere and extern in this file since could be included multiple times 
*/
extern void interface_saver(client interface i2c_master_if i);
extern void ctrlPort();

/* I2C interface ports */
extern port p_scl;
extern port p_sda;

#define USER_MAIN_DECLARATIONS \
    interface i2c_master_if i2c[1];

#define USER_MAIN_CORES on tile[0]: {\
                                        ctrlPort();\
                                        i2c_master(i2c, 1, p_scl, p_sda, 10);\
                                    }\
                        on tile[1]: {\
                                        interface_saver(i2c[0]);\
                                        /*unsafe\
                                        {\
                                            i_i2c_client = i2c[0];\
                                        }*/\
                                    }
#endif

#endif
