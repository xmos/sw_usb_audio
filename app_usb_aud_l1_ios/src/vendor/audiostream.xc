#include "port32A.h"

/* Functions that handle functions that must occur on stream 
 * start/stop e.g. DAC mute/un-mute.
 * These need implementing for a specific design.
 *
 * Implementations for the L1 USB Audio Reference Design 
 */

/* Any actions required for stream start e.g. DAC un-mute - run every 
 * stream start.
 * For L1 USB Audio Reference Design we illuminate LED B (connected 
 * to port 32A)
 */
void AudioStreamStart(void) {
    port32A_set(P32A_LED_B);
}

/* Any actions required on stream stop e.g. DAC mute - run every
 * stream stop 
 * For L1 USB Audio Reference Design we extinguish LED B (connected
 * to port 32A)
 */
void AudioStreamStop(void) {
    port32A_unset(P32A_LED_B);
}

