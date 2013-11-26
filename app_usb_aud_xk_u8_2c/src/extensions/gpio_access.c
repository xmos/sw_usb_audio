#include "gpio_access.h"
#include "swlock.h"
#include <xs1.h>

swlock_t gpo_swlock = SWLOCK_INITIAL_VALUE;

void port32A_peek(unsigned *x)
{
    // Wrapped in lock to ensure it's safe from the audio and iOS threads
    swlock_acquire(&gpo_swlock);
    asm volatile("peek %0, res[%1]":"=r"(*x):"r"(XS1_PORT_32A));
    swlock_release(&gpo_swlock);
}

void port32A_out(unsigned x)
{
    // Wrapped in lock to ensure it's safe from the audio and iOS threads
    swlock_acquire(&gpo_swlock);
    asm volatile("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
    swlock_release(&gpo_swlock);
}
