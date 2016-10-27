#ifdef TESTGEN
#include <platform.h>
#include <xs1.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <xclib.h>
#include <stdint.h>
#include <print.h>

#include "devicedefines.h"
#include "xua_audio.h"

/* TESTGEN simply uses the UserBufferManagement() function to loop back the USB samples from host back to the host via USB 
 * (starting at index NUM_PDM_MICS)
 * 
 * The processing is so simple that the use of the audManage_if is not required 
*/

/* sampsFromUsbToAudio: The sample frame the device has recived from the host and is going to play to the output audio interfaces */
/* sampsFromAudioToUsb: The sample frame that was received from the audio interfaces and that the device is going to send to the host */
/* Note: this is called from audio_io() */
#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[], client audManage_if i_audMan)
{
    sampsFromAudioToUsb[NUM_PDM_MICS]   = sampsFromUsbToAudio[0];                 
    sampsFromAudioToUsb[NUM_PDM_MICS+1] = sampsFromUsbToAudio[1];                 
} 

#endif /* TESTGEN */
