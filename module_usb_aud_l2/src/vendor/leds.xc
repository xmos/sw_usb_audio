
#include <xs1.h>
#include <print.h>

extern out port p_led;

/* Current value of LEDs */
unsigned short ledValue = 0;

void SwitchActiveLed(unsigned value)
{
    ledValue &= 0xfffe;
    ledValue |= value;
    p_led <: ledValue;
}

void SwitchClockLed(unsigned value)
{
    ledValue &= 0xfffd;
    ledValue |= value<<1;
    p_led <: ledValue;
}
