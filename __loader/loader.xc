#include <xs1.h>

extern void readFlashDataPage(unsigned addr);

int dpVersion;
unsigned imgAdr;

in port p_sw = XS1_PORT_4D;

/* Load image based on a switch 
 * Expecting:
   - 0: usb audio
   - 1: ipod dock
   - 2: usb audio upgrade
   - 3: ipod dock upgrade

if an upgrade images exists for the desired function boot this, else use the factory image for the desired functionality */

void init(void) 
{
    unsigned tmp;

    dpVersion = 0;      /* Default to USB Audio */

    p_sw :>  tmp;

    if((tmp & 0b1000)== 0b1000)
    {
        dpVersion = 1; /* iPod Dock */
    }
}

int checkCandidateImageVersion(int v) 
{
    /* We assume higher versions get priority.. */
    return (v & 1) == dpVersion;
}

void recordCandidateImage(int v, unsigned adr) 
{
      imgAdr = adr;
}

unsigned reportSelectedImage(void) 
{
      return imgAdr;
}
