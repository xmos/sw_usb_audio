#include "gpio_access.h"
#include "swlock.h"
#include <xs1.h>
#include <xcore/port.h>
#include <xk_audio_216_mc_ab/gpio_access.h>

void p_gpio_lock()
{
    aud_216_p_gpio_lock();
}

void p_gpio_unlock()
{
    aud_216_p_gpio_unlock();
}

unsigned p_gpio_peek()
{
    return aud_216_p_gpio_peek();
}

void p_gpio_out(unsigned x)
{
    aud_216_p_gpio_out(x);
}

void set_gpio(unsigned bit, unsigned value)
{
    aud_216_set_gpio(bit, value);
}


