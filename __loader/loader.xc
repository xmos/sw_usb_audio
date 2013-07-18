#include <xs1.h>

extern void readFlashDataPage(unsigned addr);

int dpVersion;
unsigned imgAdr;

in port p_sw = XS1_PORT_4D;

void init(void) 
{
    unsigned tmp;

    dpVersion = 0;

    p_sw :>  tmp;

    if((tmp & 0b1000)== 0b1000)
    {
        dpVersion = 1;
    }
}

int checkCandidateImageVersion(int v) 
{
    return v == dpVersion;
}

void recordCandidateImage(int v, unsigned adr) 
{
      imgAdr = adr;
}

unsigned reportSelectedImage(void) 
{
      return imgAdr;
}
