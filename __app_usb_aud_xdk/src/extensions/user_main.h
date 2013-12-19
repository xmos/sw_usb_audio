
#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

void genclock();

#define USER_MAIN_CORES \
    on tile[2] : genclock();

#endif
