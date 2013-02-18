
//extern in port p_but;
#include <print.h>
#include <xclib.h>

extern unsigned g_adcVal;

/* 
 * Simple *example* of how to potentially used ADC to control a volume (Via HID)
 *
 * Please note this is an *example* only
 *
 * Volume in the range 0x8100 (-127dB) to 0x0000 (0dD) - 0x8000 is mute special case
 * Resolution is 0x0100;
 * i.e. 32768 to 0 in steps of 256.
 *
 * ADC in the range 0x0 to 7fff  
*/

#define THRESH 3

void Vendor_ReadHIDButtons(unsigned char hidData[])
{
    int tmp;
    unsigned currentVol;
    unsigned adcVal;
    int diff;
    asm("ldw %0, dp[volsOut]":"=r"(tmp));

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
