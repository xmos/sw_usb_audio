#include <xs1.h>
#if 0
void do_volt_tweak();

extern void user_init(void) __attribute__((weak));

static void user_init_constructor(void) __attribute__((constructor));

static void user_init_constructor(void) {
   
   if (get_local_tile_id() == 0)
   {
        //do_volt_tweak();  
    }
}
#endif
