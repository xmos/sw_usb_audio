#ifndef USER_MAIN_H
#define USER_MAIN_H

#ifdef __XC__

void UserHIDPoll();

#define USER_MAIN_CORES on tile[XUD_TILE]: {\
                                        UserHIDPoll();\
                                    }

#endif

#endif
