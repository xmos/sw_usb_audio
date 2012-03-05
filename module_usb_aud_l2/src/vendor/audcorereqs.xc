
#include <xs1.h>
#include "devicedefines.h"
#include "vendorcmds.h"

#include <print.h>

#ifdef VENDOR_AUDCORE_REQS

void SwitchActiveLed(unsigned value);

int VendorAudCoreReqs(unsigned cmd, chanend c_clk_ctl)
{
    if(cmd == HOST_ACTIVE)
    {
        int valid;
		valid = inuint(c_clk_ctl);
	    chkct(c_clk_ctl, XS1_CT_END);

        SwitchActiveLed(valid);
    }

    /* Return 0 for no error */
    return 0;
}
#endif
