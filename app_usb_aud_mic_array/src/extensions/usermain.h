
#ifndef _USERCODE_H_
#define _USERCODE_H_

#ifndef __STDC__
#include "xua_dsp.h"

#include <xscope.h>

#if CONTROL
#include "control.h"
#define NUM_MODULES     1
#endif

[[combinable]]
void dsp_control(client dsp_ctrl_if i_dsp_ctrl);
[[combinable]]
void xscope_server(chanend c_xscope, client interface control i_module[1]);

#define DSP_CONTROL_TASK    on tile[PDM_TILE].core[0]: dsp_control(i_dsp_ctrl[0]);

/* Prototype for our custom genclock() task */
void genclock();

// TODO User NUM_DSP_CTRL_INTS

#define   USER_MAIN_DECLARATIONS \
            chan c_xscope; \
            interface control i_modules[NUM_MODULES]; \
            interface control i_modules_dummy[NUM_MODULES];

#ifndef XVSM 
#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on tile[PDM_TILE].core[0]: user_pdm_process(i_mic_process); 
#else

#define USER_MAIN_CORES \
            on tile[1] : genclock(); \
            on stdcore[AUDIO_IO_TILE] : dsp_process(i_dsp, i_dsp_ctrl, 1, i_modules, NUM_MODULES); \
            on tile[PDM_TILE].core[0]:  user_pdm_process(i_mic_process); \
            xscope_host_data(c_xscope); \
            on tile[PDM_TILE]:  xscope_server(c_xscope, i_modules); \
            DSP_CONTROL_TASK
/* xgdb -ex 'conn --xscope-realtime --xscope-port 127.0.0.1:10101' */

#endif
#endif
#endif
