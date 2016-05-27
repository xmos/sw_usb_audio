
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifdef XVSM
    #define VENDOR_REQUESTS_PARAMS     i_modules
    #define VENDOR_REQUESTS_PARAMS_DEC CLIENT_INTERFACE(control, i_modules[1])      /* TODO NUM_MODULES */
#endif

#ifndef __STDC__

#include "xua_audio.h"

/* Prototype for our custom genclock() task */
void genclock();

#ifndef XVSM 
    #define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); 
#else

    #include "xvsm_dsp.h"
    #include "control.h"

    [[combinable]]
    void dsp_control(client dsp_ctrl_if i_dsp_ctrl);
    void dsp_buff(server audManage_if i_manAud, client dsp_if i_dsp);

    #define USER_MAIN_DECLARATIONS  \
        interface dsp_if i_dsp; \
        interface dsp_ctrl_if i_dsp_ctrl[1]; /* TODO NUM_DSP_CTRL_INTERFACES */ \
        interface control i_modules[1];      /* TODO NUM_MODULES */


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
