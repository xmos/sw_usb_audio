#include "archU_powerSaving.h"

extern void user_init(void) __attribute__((weak));

static void user_init_constructor(void) __attribute__((constructor));

static void user_init_constructor(void)
{
#if(XUD_SERIES_SUPPORT == 1)
    archU_powerSaving();
#endif
}
