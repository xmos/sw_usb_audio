/* Functions that handle functions that must occur on stream
 * start/stop e.g. DAC mute/un-mute.
 * These need implementing for a specific design.
 *
 * Implementations for the SU1 Core board with audio slice
 */

/* Any actions required for stream start e.g. DAC un-mute - run every
 * stream start.
 *
 * For U8 Multifunction Audio Board we illuminate LED B.
 *
 */
#include <xs1.h>
#include "gpio_defines.h"
#include "gpio_access.h"

void UserAudioStreamStart(void)
{
    unsigned x;

    port32A_lock_peek(x);

    x |= P_GPIO_LEDB;
    x &= (~P_GPIO_AUD_MUTE);

    port32A_out_unlock(x);
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop
 *
 * For U8 Multi-function Audio Board we extinguish LED B (connected
 * to port 32A)
 *
 */
void UserAudioStreamStop(void)
{
    unsigned x;

    port32A_lock_peek(x);

    x &= (~P_GPIO_LEDB);
    x |= (P_GPIO_AUD_MUTE);

    port32A_out_unlock(x);
}
