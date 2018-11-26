#include <xclib.h>
#include "devicedefines.h"

extern unsigned g_adcVal;

/*
 * Simple *example* of how to potentially used ADC to control a volume (Via HID)
 *
 * Please note this is an *example* only.  An absolute ADC input does not really serve
 * as a good input to a relative HID volume control
 *
 * ADC in the range 0x0 to 7fff
=======
 * as a good input to a relative HID volume control!
 *
 * If ADC around halfway then no change to volume
 * If ADC above halfway then volume up
 * If ADC below halfway then volume down
*/

#define THRESH    600
#define ADC_MAX   4096
#define ADC_MIN   0

void Vendor_ReadHIDButtons(unsigned char hidData[])
{
    unsigned adcVal;
    int diff;

    hidData[0] = 0;

#if defined(ADC_VOL_CONTROL) && (ADC_VOL_CONTROL == 1)
    adcVal = g_adcVal >> 20;

    if(adcVal < (ADC_MIN + THRESH))
    {
        /* Volume down */
        hidData[0] = 0x10;
    }
    else if (adcVal > (ADC_MAX - THRESH))
    {
        /* Volume up */
        hidData[0] = 0x08;
    }
#endif
}
