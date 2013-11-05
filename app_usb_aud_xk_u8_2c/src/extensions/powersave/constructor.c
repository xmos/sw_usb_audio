#include "archU_powerSaving.h"

extern void user_init(void) __attribute__((weak));

static void user_init_constructor(void) __attribute__((constructor));

static void user_init_constructor(void)
{
#ifdef XUD_ON_U_SERIES
    archU_powerSaving();
#endif
}
