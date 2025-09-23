// Copyright 2022-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#include <print.h>
#include "xua.h"

on tile[XUA_XUD_TILE_NUM]: in port p_vbus = XS1_PORT_4C;

unsigned int XUD_HAL_GetVBusState(void)
{
    unsigned vBus;
    p_vbus :> vBus;
    return !vBus;
}

