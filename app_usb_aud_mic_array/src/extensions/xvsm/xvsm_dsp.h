

#ifndef _DSP_H_
#define _DSP_H_
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


/* Control interface and task */
typedef interface dsp_ctrl_if
{
    int setControl(unsigned moduleId, unsigned control, unsigned setting);
} dsp_ctrl_if;


void dsp_process(server dsp_if i_dsp, server dsp_ctrl_if i_dsp_ctrl[numDspCtrlInts], unsigned numDspCtrlInts);


#endif

