#ifdef IAP
#include "iap_user.h"
#endif
#include <print.h>

/* Select Apple connector */
void SelectUSBApple(void)
{
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
}

#include <xs1.h>
/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    unsigned tmp = 0;

    return 0;

}
