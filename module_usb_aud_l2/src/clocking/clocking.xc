/* These functions must be implemented for the clocking arrangement of specific design */

#include "pll.h"

void ClockingInit(chanend ?c)
{
    /* For L2 reference design initialise the external fractional-n clock multiplier - see pll.xc */
    PllInit(c);
}

void ClockingConfig(unsigned mClkFreq, chanend ?c)
{
    /* For L2 reference design configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
    PllMult(mClkFreq/300, c);
}
