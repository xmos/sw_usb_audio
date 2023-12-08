#include <platform.h>
#include <xs1.h>
#include "i2s.h"
#include <print.h>
#include <stdlib.h>

#ifndef EXTRA_I2S_CHAN_COUNT_IN
#define EXTRA_I2S_CHAN_COUNT_IN  (2)
#endif

#ifndef EXTRA_I2S_CHAN_INDEX_IN
#define EXTRA_I2S_CHAN_INDEX_IN  (0)
#endif

#ifndef EXTRA_I2S_CHAN_COUNT_OUT
#define EXTRA_I2S_CHAN_COUNT_OUT (0)
#endif

#ifndef EXTRA_I2S_CHAN_INDEX_OUT
#define EXTRA_I2S_CHAN_INDEX_OUT (0)
#endif

#define DATA_BITS (32)

unsafe chanend uc_i2s;

void UserBufferManagementInit(unsigned sampFreq)
{
    (void)sampFreq;
}

unsigned counter = 0;

#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[])
{

    unsafe
    {
        outuint((chanend) uc_i2s, 1);

        for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_OUT; i++)
        {
            outuint((chanend)uc_i2s,sampsFromUsbToAudio[i + EXTRA_I2S_CHAN_INDEX_OUT]);
        }
        outct((chanend)uc_i2s, XS1_CT_END);
        for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
        {
            sampsFromAudioToUsb[i + EXTRA_I2S_CHAN_INDEX_IN] = inuint((chanend) uc_i2s);
        }

        chkct((chanend)uc_i2s, XS1_CT_END);
    }
}


void i2s_data(server i2s_frame_callback_if i_i2s, chanend c)
{
    unsigned x;
    unsigned samplesIn[EXTRA_I2S_CHAN_COUNT_IN];
    unsigned samplesOut[EXTRA_I2S_CHAN_COUNT_OUT];

    while (1)
    {
        select
        {
            case inuint_byref(c, x):
#pragma loop unroll
                for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_OUT; i++)
                {
                    samplesOut[i] = inuint(c);
                }
                chkct(c, XS1_CT_END);

#pragma loop unroll
                for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
                {
                    outuint(c, samplesIn[i]);
                }
                outct(c, XS1_CT_END);

                break;

            case i_i2s.init(i2s_config_t &?i2s_config, tdm_config_t &?tdm_config):
                i2s_config.mode = I2S_MODE_I2S;
                break;

            case i_i2s.restart_check() -> i2s_restart_t restart:
                // Inform the I2S slave whether it should restart or exit
                restart = I2S_NO_RESTART;
                break;

            case i_i2s.receive(size_t num_in, int32_t samples[num_in]):
#pragma loop unroll
                for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_IN; i++)
                {
                    samplesIn[i] = samples[i];
                }
                break;

            case i_i2s.send(size_t num_out, int32_t samples[num_out]):
#pragma loop unroll
                for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_OUT; i++)
                {
                    samples[i] = samplesOut[i];
                }
                break;
        }
    }
}

on tile[1]: in buffered port:32 p_i2s_din[1] = {XS1_PORT_1M}; // X1D36
on tile[1]: in port p_i2s_bclk = XS1_PORT_1O;                 // X1D38
on tile[1]: in buffered port:32 p_i2s_lrclk = XS1_PORT_1P;    // X1D39

on tile[1]: clock clk_bclk = XS1_CLKBLK_1;

void i2s_driver(chanend c)
{
    interface i2s_frame_callback_if i_i2s;

    par
    {
        i2s_frame_slave(i_i2s, null, 0, p_i2s_din, 1, DATA_BITS, p_i2s_bclk, p_i2s_lrclk, clk_bclk);
        i2s_data(i_i2s, c);
    }

    return;
}
