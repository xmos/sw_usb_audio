#ifndef _USER_MAIN_H_
#define _USER_MAIN_H_

#ifdef IAP_EA_NATIVE_TRANS
#include <xccompat.h>
void ea_protocol_demo(chanend c_ea_data);

#define USER_MAIN_CORES \
    on tile[1] : ea_protocol_demo(c_ea_data);

#endif /* IAP_EA_NATIVE_TRANS */

#endif /* _USER_MAIN_H_ */
