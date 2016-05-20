
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifndef __STDC__
#include "xua_audio.h"
#include "xvsm_dsp.h"

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl);
void dsp_buff(server audManage_if i_manAud, client dsp_if i_dsp);

/* Prototype for our custom genclock() task */
void genclock();

#ifndef XVSM 
    #define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); 
#else

    #define USER_MAIN_DECLARATIONS  \
        interface dsp_if i_dsp; \
        interface dsp_ctrl_if i_dsp_ctrl[1]; // TODO NUM_DSP_CTRL_INTERFACES


    #ifdef MIC_PROCESSING_USE_INTERFACE
        #define USER_MAIN_CORES \
            on tile[1]: genclock(); \
            on tile[PDM_TILE]: dsp_process(i_dsp, i_dsp_ctrl, 1); \
            on tile[PDM_TILE]: dsp_buff(i_audMan, i_dsp); \
            on tile[PDM_TILE]: dsp_control(i_dsp_ctrl[0]); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); 
    #else
        #define USER_MAIN_CORES \
            on tile[1]: genclock(); \
            on tile[PDM_TILE]: dsp_process(i_dsp, i_dsp_ctrl, 1); \
            on tile[PDM_TILE]: dsp_buff(i_audMan, i_dsp); \
            on tile[PDM_TILE]: dsp_control(i_dsp_ctrl[0]); 
    #endif
#endif

#endif
#endif
