
#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#if !(defined(SPDIF_RX) || defined(ADAT_RX))
void genclock();

#define USER_MAIN_CORES \
    on tile[1] : genclock();

#endif
#endif
