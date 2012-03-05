#ifndef _AUDIOSTREAM_H_
#define _AUDIOSTREAM_H_

/* Functions that handle functions that must occur on stream start/stop e.g. DAC mute/un-mute
 * These need implementing for a specific design.
 *
 * Implementations for the L2 USB Audio Reference Design 
 */

/* Any actions required for stream start e.g. DAC un-mute - run every stream start 
 */
void AudioStreamStart(void)
{
   // Do nothing... 
}

/* Any actions required on stream stop e.g. DAC mute - run every steam stop 
 */
void AudioStreamStop(void)
{
   // Do nothing... 
}
#endif

