#ifndef USER_MAIN_H
#define USER_MAIN_H

#ifdef __XC__

#if HID_CONTROLS > 0
void UserHIDPoll();

#define USER_MAIN_CORES on tile[XUD_TILE]: {\
                                        UserHIDPoll();\
                                    }
#endif  // HID_CONTROLS > 0

#endif

#endif
