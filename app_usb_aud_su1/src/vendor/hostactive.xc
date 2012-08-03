

#include <xs1.h>
#include "devicedefines.h"
#include "port32A.h"

#ifdef HOST_ACTIVE_CALL

void VendorHostActive(int active)
{
    int x;
 
    if(active)
    {
        x = port32A_peek();
        x |= P32A_LED_A;
        port32A_out(x);  
    }
    else
    {
        x = port32A_peek();
        x &= (~P32A_LED_A);
        port32A_out(x);
    }  
}


#endif
