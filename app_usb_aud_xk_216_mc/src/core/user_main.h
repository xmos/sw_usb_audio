#ifndef USER_MAIN_H
#define USER_MAIN_H

#ifdef __XC__

#include <xk_audio_216_mc_ab/ports.h>
#if HID_CONTROLS > 0
void UserHIDPoll();

#define USER_MAIN_CORES on tile[XUD_TILE]: {\
                                        UserHIDPoll();\
                                    }
#endif  // HID_CONTROLS > 0

#endif

#endif
