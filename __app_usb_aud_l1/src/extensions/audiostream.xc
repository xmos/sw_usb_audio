#include <xs1.h>
#include "port32A.h"

/* Functions that handle functions that must occur on stream
 * start/stop e.g. DAC mute/un-mute.These need implementing
 * for a specific design.
 *
 * Implementations for the L1 USB Audio Reference Design
 */

/* Any actions required for stream start e.g. DAC un-mute - run every
 * stream start.
 *
 * For L1 USB Audio Reference Design we illuminate LED B (connected
 * to port 32A)
 *
 * Since this port is shared with other functionality inline assembly
 * is used to access the port resource.
 */
void UserAudioStreamStart(void)
{
    int x;

    /* Peek at current port value using port 32A resource ID */
    asm("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));

    x |= P32A_LED_B;

    /* Output to port */
    asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop
 * For L1 USB Audio Reference Design we extinguish LED B (connected
 * to port 32A)
 */
void UserAudioStreamStop(void)
{
    int x;

    asm("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));
    x &= (~P32A_LED_B);
    asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
}

