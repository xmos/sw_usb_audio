#include <print.h>
#include "xua.h"

on tile[XUD_TILE]: in port p_vbus = XS1_PORT_4C;

unsigned int XUD_HAL_GetVBusState(void)
{
    unsigned vBus;
    p_vbus :> vBus;
    return !vBus;
}

