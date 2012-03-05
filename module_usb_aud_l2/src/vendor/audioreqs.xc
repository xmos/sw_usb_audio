#include "devicedefines.h"
#include "xud.h"

#if defined (VENDOR_AUDIO_REQS) || defined (HOST_ACTIVE_CALL)

unsigned clkchan;

void VendorAudioRequestsInit(chanend c_aud_ctl, chanend ?c_mix_ctl, chanend ?c_clk_ctl)
{
    /* Store c_clk_ctl for use later */
    asm("stw %0, dp[clkchan]":: "r" (c_clk_ctl));
}

int VendorAudioRequests(XUD_ep ep0_out, XUD_ep ep0_in, unsigned char bRequest, unsigned char cs, 
    unsigned char cn, unsigned short unitId, unsigned char direction, chanend c_audioControl, 
    chanend ?c_mix_ctl, chanend ?c_clk_ctl)
{
    /* Return 0 for handled with no error 
     *        1 for not handled 
     */
    return 1;
}
#endif

