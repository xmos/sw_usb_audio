#include <xs1.h>
#include "devicedefines.h"


//:codec_init
void AudioHwInit(chanend ?c_codec) 
{
    return;
}
//:

//:codec_config
/* Configures the CODEC for the required sample frequency.  
 * CODEC reset and frequency select are connected to port 32A
 *
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, int dsdMode)
{
    return;
}
//:
