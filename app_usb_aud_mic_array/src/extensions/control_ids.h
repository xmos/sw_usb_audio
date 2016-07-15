#include "xvsm_control.h"
#include "xvsm_vad.h"
#include "lib_voice_doa_naive.h"


#define IVL_RESID_BASE 1
#define DOA_RESID_BASE (IVL_RESID_BASE + IVL_RESID_COUNT)
#define VAD_RESID_BASE (DOA_RESID_BASE + DOA_RESID_COUNT)





