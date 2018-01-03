/* Functions that handle functions that must occur on stream
 * start/stop e.g. DAC mute/un-mute.
 * These need implementing for a specific design.
 *
 * Implementations for the SU1 Core board with audio slice
 */

/* Any actions required for stream start e.g. DAC un-mute - run every
 * stream start.
 *
 * For SU1 Core Board we illuminate LED on audio slice
 */

#include "p_gpio.h"
#include "p_gpio_defines.h"

void UserAudioStreamStart(void)
{
    int x;

    x = p_gpio_peek();
    x |= P_GPIO_LED;
    p_gpio_out(x);
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop
 * For L1 USB Audio Reference Design we extinguish LED B (connected
 * to port 32A)
 */
void UserAudioStreamStop(void)
{
    int x;

    x = p_gpio_peek();
    x &= (~P_GPIO_LED);
    p_gpio_out(x);
}

