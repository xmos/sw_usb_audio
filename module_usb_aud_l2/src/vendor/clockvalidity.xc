#include "devicedefines.h"

#ifdef CLOCK_VALIDITY_CALL
void SwitchClockLed(unsigned value);

/* This is called from ClockGen on core 1 */
void VendorClockValidity(int valid)
{
    SwitchClockLed(valid);
}
#endif
