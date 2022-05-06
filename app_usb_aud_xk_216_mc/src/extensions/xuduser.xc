#include <platform.h>
#include <xs1_su.h>
#include "app_usb_aud_xk_216_mc.h"
#include "hostactive.h"
#include "audiostream.h"

#if USB_SEL_A
#include <hwtimer.h>
#include "interrupt.h"
hwtimer_t g_rebootTimer;


#pragma select handler
void HandleRebootTimeout(timer t)
{
    unsigned pll_ctrl_val;

    /* Reset device */
    read_sswitch_reg(get_local_tile_id(), 6, pll_ctrl_val);
    pll_ctrl_val &= 0x7FFFFFFF;
    write_sswitch_reg_no_ack(get_local_tile_id(), 6, pll_ctrl_val);
    while(1);
}

#define REBOOT_TIMEOUT 20000000

void XUD_UserSuspend(void)
{
    unsigned time;

    UserAudioStreamStop();
    UserHostActive(0);

    DISABLE_INTERRUPTS();

    asm volatile("setc res[%0], %1"::"r"(g_rebootTimer),"r"(XS1_SETC_COND_NONE));
    g_rebootTimer :> time;
    time += REBOOT_TIMEOUT;

    asm volatile("setd res[%0], %1"::"r"(g_rebootTimer),"r"(time));
    asm volatile("setc res[%0], %1"::"r"(g_rebootTimer),"r"(XS1_SETC_COND_AFTER));

    set_interrupt_handler(HandleRebootTimeout, 1, g_rebootTimer, 0)
}

void XUD_UserResume(void)
{
    unsigned config;

    /* Clear the reboot interrupt */
    DISABLE_INTERRUPTS();
    asm("edu res[%0]"::"r"(g_rebootTimer));

    asm("ldw %0, dp[g_currentConfig]" : "=r" (config):);

    if(config == 1)
    {
        UserHostActive(1);
    }
}

#endif
