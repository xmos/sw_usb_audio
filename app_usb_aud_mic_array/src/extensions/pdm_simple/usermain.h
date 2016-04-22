
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifndef __STDC__

/* Prototype for our custom genclock() task */
void genclock();

#if (NUM_PDM_MICS == 0)
#define USER_MAIN_CORES \
            on tile[1] : genclock();
#else

#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); \
#endif
#endif
#endif
