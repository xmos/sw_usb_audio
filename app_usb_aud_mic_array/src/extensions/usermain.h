
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifndef __STDC__
#include "xua_dsp.h"

#if CONTROL
#include "control.h"

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl, server interface control i_modules[num_modules], const size_t num_modules);
#else
[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl);
#endif

#if CONTROL
#define DSP_CONTROL_TASK    on tile[PDM_TILE].core[0]: dsp_control(i_dsp_ctrl[0], i_modules, NUM_MODULES);
#else
#define DSP_CONTROL_TASK    on tile[PDM_TILE].core[0]: dsp_control(i_dsp_ctrl[0]);
#endif

/* Prototype for our custom genclock() task */
void genclock();

// TODO User NUM_DSP_CTRL_INTS

#ifndef XVSM 
#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); 
#else

#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on stdcore[AUDIO_IO_TILE] : dsp_process(i_dsp, i_dsp_ctrl, 1); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); \
            DSP_CONTROL_TASK
#endif
#endif
#endif
