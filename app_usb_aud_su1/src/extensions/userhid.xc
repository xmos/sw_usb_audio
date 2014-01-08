#include <xs1.h>
#include <platform.h>


on tile[0] : in port p_but       = PORT_BUT;

void UserReadHIDButtons(unsigned char hidData[])
{
    int tmp;
    p_but :> tmp;
    tmp = ~tmp;
    tmp &=3;
    hidData[0] = tmp;
}
