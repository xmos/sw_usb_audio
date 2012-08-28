
//extern in port p_but;
#include <print.h>

int lastAdcVal = 0;
extern unsigned g_adcVal;
unsigned diffcount = 0;

/* volume in the range 0x8000 to 0x0000 */
/* ADC in the range 0x0 to 0xfff */

void Vendor_ReadHIDButtons(unsigned char hidData[])
{
    int tmp;
    unsigned currentVol;
    unsigned adcVal;
    unsigned diff;
    //hidData[0] = 0;    
    asm("ldw %0, dp[volsOut]":"=r"(tmp));

    currentVol = (int) tmp;
    currentVol*=-1;
    adcVal = g_adcVal >> 20;

    if(lastAdcVal > adcVal)
    {
        diff = lastAdcVal - adcVal;
        if(diff> 5)
        {
            hidData[0] = 0x8;
    lastAdcVal = adcVal;
            printstrln("DOWN");
        }
        diffcount = 0;
    }
    else if(adcVal > lastAdcVal)
    {
        diff = adcVal - lastAdcVal;
        if(diff > 4)
        {
              hidData[0] = 0x10;
    lastAdcVal = adcVal;
            printstrln("UP");
        diffcount = 0;
    }
    else
    {
        diffcount++;
        if(diffcount == 5)
        {
            diffcount = 0;
            hidData[0] = 0;
        }   
    }
 }    

}
