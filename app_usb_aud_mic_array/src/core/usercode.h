
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifndef __STDC__
#include "xua_dsp.h"

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl);

/* Prototype for our custom genclock() task */
void genclock();

#if (NUM_PDM_MICS == 0)
#define USER_MAIN_CORES \
            on tile[1] : genclock();
#else

#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); \
            on tile[PDM_TILE].core[0]: dsp_control(i_dsp_ctrl[0]);

#endif
#endif
#endif
