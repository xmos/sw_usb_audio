/* Functions that handle functions that must occur on stream 
 * start/stop e.g. DAC mute/un-mute.
 * These need implementing for a specific design.
 *
 * Implementations for the SU1 Core board with audio slice
 */

/* Any actions required for stream start e.g. DAC un-mute - run every 
 * stream start.
 */

#include "p_gpio.h"
#include "p_gpio_defines.h"

void UserAudioStreamStart(void) 
{
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop 
 */
void UserAudioStreamStop(void) 
{
}

