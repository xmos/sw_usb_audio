#include <xs1.h>

extern void readFlashDataPage(unsigned addr);

in port p_sw = XS1_PORT_4D;

unsigned loadmagic()
{
    unsigned x;
    asm("ldw %0, %1[0]" : "=r"(x):  "r"(0x1ffc8));
    return x;
}  

void storemagic(unsigned x)
{
    asm("stw %0, %1[0]" :: "r"(x), "r"(0x1ffc8));
}   

int dpVersion;
unsigned imgAdr;

//in port p_sw = XS1_PORT_4D;

/* Load image based on a switch
 * Expecting:
   - 1: ipod dock
   - 0: usb audio (MFI)
   - 2: usb audio (Non MFI for B connector)

TODO if an upgrade images exists for the desired function boot this, else use the factory image for the desired functionality */

#define IMAGE_NUM_DOCK        0
#define IMAGE_NUM_USB_AUD_MFI 1
#define IMAGE_NUM_USB_AUD     2

void init(void)
{
    unsigned tmp;
    unsigned switchVal;

    p_sw :>  switchVal;

    dpVersion = IMAGE_NUM_DOCK;      /* Default to iPod dock */

    if((switchVal & 0b1000)== 0b0000)
    {
        dpVersion = IMAGE_NUM_USB_AUD;  /* USB Audio (B connector) */
    }
    else
    {
        tmp = loadmagic();

        if(tmp == 0xDEAD)
        {
            dpVersion = IMAGE_NUM_USB_AUD_MFI;  /* USB Audio MFI*/
        }
    }
    storemagic(0);
}

int checkCandidateImageVersion(int v)
{
    /* We assume higher versions get priority.. */
    return (v) == dpVersion;
}

void recordCandidateImage(int v, unsigned adr)
{
      imgAdr = adr;
}

unsigned reportSelectedImage(void)
{
      return imgAdr;
}
