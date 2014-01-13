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

#include <xs1.h>
#include <platform.h>

on tile[0] : out port p_led     = XS1_PORT_1B;

void UserAudioStreamStart(void)
{

    p_led <: 1;
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop
 */
void UserAudioStreamStop(void)
{
    int x;

    p_led <: 0;
}

