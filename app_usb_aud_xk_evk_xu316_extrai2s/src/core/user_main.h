
#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef __XC__
void i2s_driver(chanend c);
void AudioHwRemote(chanend c);

extern unsafe chanend uc_i2s;
extern unsafe chanend uc_audiohw;


#define USER_MAIN_DECLARATIONS chan c_i2s; chan c_audiohw;

#define USER_MAIN_CORES on tile[1]: {\
                                        par\
                                        {\
                                            i2s_driver(c_i2s);\
                                            unsafe{\
                                                uc_i2s = (chanend) c_i2s;\
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

