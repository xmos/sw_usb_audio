#include <xs1.h>
#include "devicedefines.h"
#include "port32A.h"

void UserHostActive(int active)
{
    int x;

    /* Illuminate LED A on host active. Since this port is shared with other
     * functionality inlne asm is used to access port
     */
    if(active)
    {
        /* Peek at current port value using port 32A resource ID */
        asm("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));

        x |= P32A_LED_A;

        /* Output to port */
        asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
    }
    else
    {
        asm("peek %0, res[%1]":"=r"(x):"r"(XS1_PORT_32A));
        x &= (~P32A_LED_A);
        asm("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(x));
    }
}
