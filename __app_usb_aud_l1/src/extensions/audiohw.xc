#include <xs1.h>
#include <print.h>
#include "port32A.h"
#include "devicedefines.h"

// Port 32A helpers
#define PORT32A_PEEK(X) {asm("peek %0, res[%1]":"=r"(X):"r"(XS1_PORT_32A));}
#define PORT32A_OUT(X)  {asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(X));}

//:audiohw_init
void AudioHwInit(chanend ?c_codec)
{
    return;
}
//:

//:audiohw_config
/* Configures the CODEC for the required sample frequency.
 * CODEC reset and frequency select are connected to port 32A
 *
 * Port 32A is shared with other functionality (LEDs etc) so we
 * access via inline assembly. We also take care to retain the
 * state of the other bits.
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned samRes_DAC, unsigned samRes_ADC)
{
    timer t;
    unsigned time;
    unsigned tmp;

    /* Put codec in reset and set master clock select appropriately */

    /* Read current port output */
    PORT32A_PEEK(tmp);

    /* Put CODEC reset line low */
    tmp &= (~P32A_COD_RST);

    if ((samFreq % 22050) == 0)
    {
        /* Frequency select low for 441000 etc */
        tmp &= (~P32A_CLK_SEL);
    }
    else //if((samFreq % 24000) == 0)
    {
        /* Frequency select high for 48000 etc */
        tmp |= P32A_CLK_SEL;
    }

    PORT32A_OUT(tmp);

    /* Hold in reset for 2ms */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* Codec out of reset */
    PORT32A_PEEK(tmp);
    tmp |= P32A_COD_RST;
    PORT32A_OUT(tmp);
}
//:
