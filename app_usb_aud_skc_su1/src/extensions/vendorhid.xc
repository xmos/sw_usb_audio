
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
 *
 * If ADC around halfway then no change to volume
 * If ADC above halfway then volume up
 * If ADC below halfway then volume down
*/

#define THRESH 3

void Vendor_ReadHIDButtons(unsigned char hidData[])
{
    int tmp;
    unsigned currentVol;
    unsigned adcVal;
    int diff;

    hidData[0] = 0;

    currentVol = (int) tmp;
    currentVol*=-1;
    adcVal = g_adcVal >> 20;

    /* Get ADC to same scale as Volume */
    adcVal *= 8 ;

    /* Volume resolution is 256 */
    adcVal >>= 8;       // /256;
    currentVol >>= 8;   // /256;

    diff = adcVal - currentVol;
 
    // Abs   
    if(diff < 0)
        diff*=-1;

    if(diff>THRESH)
    {
        if((adcVal) < currentVol)
        {
            hidData[0] = 0x8;
        }
        else if ((adcVal)> currentVol)
        {
            hidData[0] = 0x10;
        }
    }
}
