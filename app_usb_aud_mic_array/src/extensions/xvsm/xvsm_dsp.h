
#ifndef _XVSM_DSP_H_
#define _XVSM_DSP_H_


#define CONTROL 1
#include "control.h"

/* Processing interface and task */
/* Interface to transfer block of samples to/from DSP task */
typedef interface dsp_if
{
    [[guarded]]
    void transfer_buffers(int * unsafe in_aud_buf, int * unsafe in_usb_buf,
                            int * unsafe out_usb_buf, int * unsafe out_aud_buf);

    [[guarded]]
    void transfer_samples(int in_mic_buf[], int in_spk_buf[], int out_mic_buf[], int out_spk_buf[]);

} dsp_if;


#if 0
/* Control interface and task */
typedef interface dsp_ctrl_if
{
    int setControl(unsigned moduleId, unsigned control, unsigned setting);
} dsp_ctrl_if;
#endif

void dsp_process(server dsp_if i_dsp
#if CONTROL
        , server interface control i_control, const size_t num_modules
#endif
);


// TODO move me
typedef enum vadStatet
{
    VAD_IDLE,
    VAD_DETECT,
    VAD_INVOICE,
    VAD_TIMEOUT
} vadState_t;

#endif

