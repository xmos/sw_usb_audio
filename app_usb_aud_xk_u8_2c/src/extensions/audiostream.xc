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

void UserAudioStreamStart(void)
{
    unsigned x;

    asm volatile ("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));

    x |= P_GPIO_LEDB;

    asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
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

    asm volatile ("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));

    x &= (~P_GPIO_LEDB);

    asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
}
