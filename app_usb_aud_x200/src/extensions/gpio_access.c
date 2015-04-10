#include "gpio_access.h"
#include "swlock.h"
#include <xs1.h>

swlock_t gpo_swlock = SWLOCK_INITIAL_VALUE;

void p_gpio_lock()
{
    swlock_acquire(&gpo_swlock);
}

void p_gpio_unlock()
{
    swlock_release(&gpo_swlock);
}

unsigned p_gpio_peek()
{
    unsigned portId, x;
   
    // Wrapped in lock to ensure it's safe from multiple logical cores
    swlock_acquire(&gpo_swlock);

    asm("ldw %0, dp[p_gpio]":"=r"(portId));                        
    asm volatile("peek %0, res[%1]":"=r"(x):"r"(portId));

    return x;
}

void p_gpio_out(unsigned x)
{
    unsigned portId;
    
    asm("ldw %0, dp[p_gpio]":"=r"(portId));                        
    asm volatile("out res[%0], %1"::"r"(portId),"r"(x));
    
    // Wrapped in lock to ensure it's safe from multiple logical cores
    swlock_release(&gpo_swlock);
}
