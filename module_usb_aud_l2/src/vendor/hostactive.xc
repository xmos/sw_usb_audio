
#include <xs1.h>
#include <print.h>
#include "devicedefines.h"
#include "vendorcmds.h"

/* Example implementation of the VendorHostActive() call for the L2 USB Audio Class 2.0 Reference design board
 *
 * This is called from endpoint0 thread (on core 0).  
 * The c_clk_ctl channel is used to commicate to the clockgen thread on core 1 (where the LEDS are)
 *
 * Note: We require AudioRequestsInit() to have saved the chanend 
 */

extern unsigned clkchan;

#ifdef HOST_ACTIVE_CALL
void VendorHostActive(int active)
{
    unsigned channel = 0;
    while(channel==0)
    {
        asm("ldw %0, dp[clkchan]" : "=r" (channel):);
    }
    asm("out res[%0], %1" ::"r"(channel), "r" (HOST_ACTIVE));
    asm("out res[%0], %1" ::"r"(channel), "r" (active));
    asm("outct res[%0], %1" ::"r"(channel), "r" (XS1_CT_END));
}
#endif

