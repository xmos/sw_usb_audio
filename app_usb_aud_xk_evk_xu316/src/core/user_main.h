// Copyright 2021-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef __XC__

#include <platform.h>

void AudioHwRemote(chanend c);

extern unsafe chanend uc_audiohw;

#define USER_MAIN_DECLARATIONS chan c_audiohw;

#define USER_MAIN_CORES on tile[1]: {\
                                        par\
                                        {\
                                            unsafe{\
                                                uc_audiohw = (chanend) c_audiohw;\
                                            }\
                                        }\
                                    }\
\
                        on tile[0]: {\
                                        par\
                                        {\
                                            AudioHwRemote(c_audiohw);\
                                        }\
                                    }
#endif

#endif
