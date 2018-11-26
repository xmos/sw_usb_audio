#include "gpio.h"
#include "hwlock.h"

hwlock_t led_hwlock = HWLOCK_NOT_ALLOCATED;
unsigned short g_led_pattern = ALL_OFF;
unsigned short g_led_mask = LED_MASK_DISABLE;

void set_led_array(unsigned short led_pattern)
{
    if (led_hwlock == HWLOCK_NOT_ALLOCATED)
    {
        // Allocate a lock the first time the LED array is used only
        led_hwlock = hwlock_alloc();
    }

    // Wrapped in lock to ensure it's safe from multiple logical cores
    hwlock_acquire(led_hwlock);

    // Set the global pattern
    g_led_pattern = led_pattern;

    // Apply the global mask onto the desired pattern
    unsigned short led_state = g_led_pattern & g_led_mask;
    // Set the new LED state
    asm volatile("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(led_state));

    hwlock_release(led_hwlock);
}

void set_led_array_mask(unsigned short led_mask)
{
    if (led_hwlock == HWLOCK_NOT_ALLOCATED)
    {
        // Allocate a lock the first time the LED array is used only
        led_hwlock = hwlock_alloc();
    }

    // Wrapped in lock to ensure it's safe from multiple logical cores
    hwlock_acquire(led_hwlock);

    // Set global mask
    g_led_mask = led_mask;

    // Update the current state of LED array with the mask applied
    unsigned short led_state = g_led_pattern & g_led_mask;
    // Set the new LED state
    asm volatile("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(led_state));

    hwlock_release(led_hwlock);
}

unsigned short get_led_array_mask()
{
    return g_led_mask;
}
