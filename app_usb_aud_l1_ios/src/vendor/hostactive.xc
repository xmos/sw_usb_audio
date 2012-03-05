#include <xs1.h>
#include "devicedefines.h"
#include "port32A.h"

#ifdef HOST_ACTIVE_CALL

void VendorHostActive(int active)
{
    if(active)
    {
        port32A_set(P32A_LED_A);
    }
    else
    {
        port32A_unset(P32A_LED_A);
    }  
}


#endif
