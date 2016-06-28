#include <platform.h>
#include <xs1.h>
#include "devicedefines.h"

#ifdef DISABLE_OTP
on tile[0]: out port p_otp_ctrl0 = XS1_PORT_16D;
on tile[1]: out port p_otp_ctrl1 = XS1_PORT_16D;

#define PWR_DOWN (1 << 14)

void tile_0_otp_off(void){
    p_otp_ctrl0 <: PWR_DOWN;
}

void tile_1_otp_off(void){
    p_otp_ctrl1 <: PWR_DOWN;
}
#endif

