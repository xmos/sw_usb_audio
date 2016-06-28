/*
 * power_save.h
 */

#ifndef POWER_SAVE_H_
#define POWER_SAVE_H_

#include "devicedefines.h"
#include <platform.h>

#ifdef DISABLE_OTP
extern void tile_0_otp_off(void);
extern void tile_1_otp_off(void);

#define DISABLE_OTP_MAIN_0 tile_0_otp_off();
#define DISABLE_OTP_MAIN_1 tile_1_otp_off();
#else
#define DISABLE_OTP_MAIN_0
#define DISABLE_OTP_MAIN_1
#endif

#ifdef SCALE_SSWITCH
#define SCALE_SSWITCH_MAIN  write_sswitch_reg(get_local_tile_id() + 1, XS1_SSWITCH_CLK_DIVIDER_NUM, 0xa);
#else
#define SCALE_SSWITCH_MAIN
#endif

#ifdef CLOCK_DOWN_TILE_1
#define CLOCK_DOWN_TILE_1_MAIN delay_milliseconds(10); write_pswitch_reg(get_local_tile_id() + 1, XS1_PSWITCH_PLL_CLK_DIVIDER_NUM, XS1_PLL_CLK_DISABLE_MASK);
#else
#define CLOCK_DOWN_TILE_1_MAIN
#endif

#define USER_MAIN_DECLARATIONS

#define USER_MAIN_CORES \
        on tile[0]: { \
            DISABLE_OTP_MAIN_0 \
            SCALE_SSWITCH_MAIN \
            CLOCK_DOWN_TILE_1_MAIN \
        } \
        on tile[1]: { \
            DISABLE_OTP_MAIN_1 \
        } \


#endif /* POWER_SAVE_H_ */
