#include <xs1.h>

void trimcode();

extern void user_init(void) __attribute__((weak));

static void user_init_constructor(void) __attribute__((constructor));

static void user_init_constructor(void) {
   
   if (get_core_id() == 0) {
       // your code here
        //set_PG2_trim(xs1_su);
        trimcode();

   }
}

