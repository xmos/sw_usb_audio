#include <platform.h>
#include <xs1.h>
#include <print.h>
#include <stdlib.h>
#include <string.h>
#include "i2s.h"
#include "src.h"
#include "xua.h"

/* TODO

- Buffering:
    - Properly under-flow and overflow from/to output FIFO
    - Only push to fifo when "locked"

- General
    - Add support for SR change
    - Seperate recording and playback SRC related defines

- Optimise:
    - Optimise for 192kHz operation

*/


#ifndef USE_ASRC
#define USE_ASRC (0)
#endif

#ifndef EXTRA_I2S_CHAN_COUNT_IN
#define EXTRA_I2S_CHAN_COUNT_IN  (2)
#endif

#ifndef EXTRA_I2S_CHAN_INDEX_IN
#define EXTRA_I2S_CHAN_INDEX_IN  (0)
#endif

#ifndef EXTRA_I2S_CHAN_COUNT_OUT
#define EXTRA_I2S_CHAN_COUNT_OUT (2)
#endif

#ifndef EXTRA_I2S_CHAN_INDEX_OUT
#define EXTRA_I2S_CHAN_INDEX_OUT (0)
#endif

#define DATA_BITS                (32)
#define SAMPLE_FREQUENCY         (48000)
#define MASTER_CLOCK_FREQUENCY   (24576000)

void exit(int);

unsafe chanend uc_i2s;

/* Note, re-using I2S data lines on MC audio board for LR and Bit clocks */

on tile[1]: out buffered port:32 p_i2s_dout[1] = {PORT_I2S_DAC1};
on tile[1]: in buffered port:32 p_i2s_din[1] =   {PORT_SPDIF_OUT};
on tile[1]: in port p_i2s_bclk =                 PORT_I2S_DAC2;
on tile[1]: in buffered port:32 p_i2s_lrclk =    PORT_I2S_DAC3;
on tile[1]: in port p_off_bclk =                 XS1_PORT_16A;
on tile[1]: clock clk_bclk =                     XS1_CLKBLK_1;

extern in port p_mclk_in;

/* TODO all these defines are shared between playback and record streams - this should be fixed */

#define     SRC_N_CHANNELS                (2)   // Total number of audio channels to be processed by SRC (minimum 1)
#define     SRC_N_INSTANCES               (1)   // Number of instances (each usually run a logical core) used to process audio (minimum 1)
#define     SRC_CHANNELS_PER_INSTANCE     (SRC_N_CHANNELS/SRC_N_INSTANCES) // Calculated number of audio channels processed by each core
#define     SRC_N_IN_SAMPLES              (4)   // Number of samples per channel in each block passed into SRC each call
                                                // Must be a power of 2 and minimum value is 4 (due to two /2 decimation stages)
#define     SRC_N_OUT_IN_RATIO_MAX        (5)   // Max ratio between samples out:in per processing step (44.1->192 is worst case)
#define     SRC_DITHER_SETTING            (0)   // Enables or disables quantisation of output with dithering to 24b
#define     SRC_MAX_NUM_SAMPS_OUT         (SRC_N_OUT_IN_RATIO_MAX * SRC_N_IN_SAMPLES)
#define     SRC_OUT_BUFF_SIZE             (SRC_CHANNELS_PER_INSTANCE * SRC_MAX_NUM_SAMPS_OUT) // Size of output buffer for SRC for each instance
#define     SRC_OUT_FIFO_SIZE             (SRC_N_CHANNELS * SRC_MAX_NUM_SAMPS_OUT * 8)        // Size of output FIFO for SRC

/* Stuff that must be defined for lib_src */
#define SSRC_N_IN_SAMPLES                 (SRC_N_IN_SAMPLES) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_ssrc.h */
#define ASRC_N_IN_SAMPLES                 (SRC_N_IN_SAMPLES) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_asrc.h */

#define SSRC_N_CHANNELS                   (SRC_CHANNELS_PER_INSTANCE) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_ssrc.h */
#define ASRC_N_CHANNELS                   (SRC_CHANNELS_PER_INSTANCE) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_asrc.h */

typedef struct fifo_f
{
    int wrPtr;
    int rdPtr;
    int size;
    int fill;
} fifo_t;

static void init_fifo(fifo_t &f, int array[size], unsigned size)
{
    f.wrPtr = size/2;
    f.rdPtr = 0;
    f.size = size;
    f.fill = size/2;

    unsafe
    {
        int * unsafe arrayPtr = &array[0];
        memset(arrayPtr, 0, size * (sizeof(array[0])));
    }
}

#pragma unsafe arrays
static inline unsigned fifo_pop(fifo_t &f, int array[], int &sample)
{
    /* Check for FIFO empty */
    if (!f.fill)
    {
        sample = 0;
        return 1;
    }

    sample = array[f.rdPtr];
    f.rdPtr++;
    f.fill--;

    /* Check for wrap */
    if (f.rdPtr >= f.size)
    {
        f.rdPtr = 0;
    }

    return 0;
}

#pragma unsafe arrays
static inline unsigned fifo_push(fifo_t &f, int array[], const int sample)
{
    /* Check for FIFO full */
    if(f.fill >= f.size)
    {
        return 1;
    }

    array[f.wrPtr] = sample;
    f.wrPtr++;
    f.fill++;

    /* Check for wrap */
    if(f.wrPtr >= f.size)
    {
        f.wrPtr = 0;
    }

    return 0;
}

#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[])
{
    unsafe
    {
        outuint((chanend) uc_i2s, 1);

        for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_OUT; i++)
        {
            outuint((chanend)uc_i2s, sampsFromUsbToAudio[i + EXTRA_I2S_CHAN_INDEX_OUT]);
        }
        outct((chanend)uc_i2s, XS1_CT_END);

        for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
        {
            sampsFromAudioToUsb[i + EXTRA_I2S_CHAN_INDEX_IN] = inuint((chanend) uc_i2s);
        }
        chkct((chanend)uc_i2s, XS1_CT_END);
    }
}

#pragma unsafe arrays
static inline int trigger_src(streaming chanend c_src[SRC_N_INSTANCES],
                                int srcInputBuff[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE],
                                fifo_t &fifo,
                                int srcOutputBuff[SRC_OUT_FIFO_SIZE], uint64_t fsRatio)
{

    int nSamps = 0;
#pragma loop unroll
    for (int i=0; i<SRC_N_INSTANCES; i++)
    {
        c_src[i] <: fsRatio;

#pragma loop unroll
        for (int j=0; j<SRC_N_IN_SAMPLES; j++)
        {
#pragma loop unroll
            for (int k=0; k<SRC_CHANNELS_PER_INSTANCE; k++)
            {
                c_src[i] <: srcInputBuff[i][j][k];
            }
        }
    }

    /* Get number of samples to receive from all SRC cores */
    /* Note, all nSamps should be equal */
#pragma loop unroll
    for (int i=0; i < SRC_N_INSTANCES; i++)
    {
        c_src[i] :> nSamps;
    }

    unsigned error = 0;
    for (int j=0; j < nSamps; j++)
    {
#pragma loop unroll
        for (int k=0; k<SRC_CHANNELS_PER_INSTANCE; k++)
        {
            int sample;
#pragma loop unroll
            for (int i=0; i<SRC_N_INSTANCES; i++)
            {
                c_src[i] :> sample;
                error |= fifo_push(fifo, srcOutputBuff, sample);
            }
            if(error)
            {

                init_fifo(fifo, srcOutputBuff, sizeof(srcOutputBuff)/sizeof(srcOutputBuff[0]));
            }
        }
    }

    return nSamps;
}

#ifndef LOG_CONTROLLER
#define LOG_CONTROLLER (0)
#endif

#if LOG_CONTROLLER
#define CONT_LOG_SIZE 5000
int e[CONT_LOG_SIZE];
int f_p[CONT_LOG_SIZE];
int f_r[CONT_LOG_SIZE];
float r_p[CONT_LOG_SIZE];
float r_r[CONT_LOG_SIZE];
int logCounter = 0;
#endif

#pragma unsafe arrays
void i2s_data(server i2s_frame_callback_if i_i2s, chanend c, streaming chanend c_src_play[SRC_N_INSTANCES], streaming chanend c_src_rec[SRC_N_INSTANCES])
{
    unsigned tmp;

    int srcInputBuff_play[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE];
    int srcInputBuff_rec[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE];

    int srcOutputBuff_play[SRC_OUT_FIFO_SIZE];
    int srcOutputBuff_rec[SRC_OUT_FIFO_SIZE];

    int sampleIdx_play = 0;
    int sampleIdx_rec = 0;

    fifo_t fifo_play;
    fifo_t fifo_rec;

    int usbCounter = 0;
    int i2sCounter = 0;

    uint64_t fsRatio = (uint64_t) (96/48) << 60;
    float floatRatio = 2.0;

    unsigned short lastPt = 0;

    int asrcCounter_play = 0;
    int asrcCounter_rec = 0;  /* Run the two asrc blocks out of phase */

    int phaseError = 0;
    int phaseErrorInt = 0;

    init_fifo(fifo_play, srcOutputBuff_play, sizeof(srcOutputBuff_play)/sizeof(srcOutputBuff_play[0]));
    init_fifo(fifo_rec, srcOutputBuff_rec, sizeof(srcOutputBuff_rec)/sizeof(srcOutputBuff_rec[0]));

    while (1)
    {
        select
        {
            case inuint_byref(c, tmp):

                /* Receive samples from USB audio (other side of the UserBufferManagement() comms */
#pragma loop unroll
                for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_OUT; i++)
                {
                    srcInputBuff_play[i/SRC_CHANNELS_PER_INSTANCE][sampleIdx_play][i % SRC_CHANNELS_PER_INSTANCE] = inuint(c);
                }
                chkct(c, XS1_CT_END);

                int error = 0;

                /* Send samples to USB audio (other side of the UserBufferManagement() comms */
#pragma loop unroll
                for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
                {
                    int sample;

                    error |= fifo_pop(fifo_rec, srcOutputBuff_rec, sample);

                    /* Send a 0 zero on FIFO error e.g. underflow */
                    if(error)
                        outuint(c, 0);
                    else
                        outuint(c, sample);
                }

                outct(c, XS1_CT_END);

                if(error)
                {
                    init_fifo(fifo_rec, srcOutputBuff_rec, sizeof(srcOutputBuff_rec)/sizeof(srcOutputBuff_rec[0]));
                }


                usbCounter++;
                sampleIdx_play++;

                if(sampleIdx_play == SRC_N_IN_SAMPLES)
                {
                    sampleIdx_play = 0;

                    if(usbCounter == 400)
                    {
                        usbCounter = 0;

                        unsigned short pt;
                        asm volatile(" getts %0, res[%1]" : "=r" (pt) : "r" (p_off_bclk));

                        /* The number of bit clocks we expect on the output i2s */
                        const unsigned short expectedDiff = 128 * 50 * 2;

                        /* The actual number of bit clocks on the output i2s */
                        int actualDiff = 0;

                        if (porttimeafter(pt, lastPt))
                        {
                            actualDiff = -(short)(lastPt - pt);
                        }
                        else
                        {
                            actualDiff = (short)(pt - lastPt);
                        }
                        lastPt = pt;

                        /* Convert ASRC sample counter to bit clock units */
                        int asrcClocks_play = asrcCounter_play * 64;

                        /* Calulate error */
                        int error = asrcClocks_play - (int)actualDiff;

                        /* Ignore any large error - most likely an SR change occurred */
                        if((error < 100) && (error > -100))
                        {
                            phaseError += error;
                            phaseErrorInt += phaseError;

                            float error_p = (float) (phaseError * 0.0000005);
                            float error_i = (float) (phaseErrorInt * 0.00000005);

                            float x = (error_p + error_i);

                            floatRatio = (2.0 + x);

                            /* Clamp ratio to 1000PPM error */
                            if(floatRatio > 2.001)
                                floatRatio = 2.001;
                            if(floatRatio < 1.999)
                                floatRatio = 1.999;

#if LOG_CONTROLLER
                            e[logCounter] = error;
                            f_p[logCounter] = fifo_play.fill;
                            f_r[logCounter] = fifo_rec.fill;
                            r_p[logCounter] = floatRatio;
                            r_r[logCounter] = ((2.0/floatRatio))/2.0;

                            logCounter++;

                            if(logCounter == CONT_LOG_SIZE)
                            {
                                for(int i = 0; i < CONT_LOG_SIZE; i++)
                                {
                                    printint(e[i]);
                                    printchar(' ');
                                    printint(f_p[i]);
                                    printchar(' ');
                                    printint(f_r[i]);
                                    printf(" %f", r_p[i]);
                                    printf(" %f\n", r_r[i]);
                                }
                                exit(1);
                            }
#endif
                            /* Convert FS ratio to fixed point */
                            fsRatio = (uint64_t) (floatRatio * (1LL << 60));
                        }

                        asrcCounter_play = 0;
                    }


                    /* Send samples to SRC tasks. This function adds returned sample to FIFO */
                    asrcCounter_play += trigger_src(c_src_play, srcInputBuff_play, fifo_play, srcOutputBuff_play, fsRatio);
                }

                break;

            case i_i2s.init(i2s_config_t &?i2s_config, tdm_config_t &?tdm_config):
                i2s_config.mode = I2S_MODE_I2S;
                i2s_config.mclk_bclk_ratio = (MASTER_CLOCK_FREQUENCY / (SAMPLE_FREQUENCY*2*DATA_BITS));
                break;

            case i_i2s.restart_check() -> i2s_restart_t restart:
                /* Inform the I2S slave whether it should restart or exit */
                restart = I2S_NO_RESTART;
                break;

            case i_i2s.receive(size_t num_in, int32_t samples[num_in]):

                /* Add to recording path ASRC input buffer */
                for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_IN; i++)
                {
                    srcInputBuff_rec[i/SRC_CHANNELS_PER_INSTANCE][sampleIdx_rec][i % SRC_CHANNELS_PER_INSTANCE] = samples[i];
                }

                sampleIdx_rec++;

                /* Trigger_src for record path */
                if(sampleIdx_rec == SRC_N_IN_SAMPLES)
                {
                    sampleIdx_rec = 0;

                    /* TODO we probably should synchronise this */
                    float xx =((2.0/floatRatio))/2.0;
                    uint64_t fsRatio2 = (uint64_t)  (xx * (1LL << 60)) ;

                    /* Note, currenly don't use the count here since we expect the record and playback rates to match*/
                    asrcCounter_rec += trigger_src(c_src_rec, srcInputBuff_rec, fifo_rec, srcOutputBuff_rec, fsRatio2);
                }

                break;

            case i_i2s.send(size_t num_out, int32_t samples[num_out]):
            {
                int error = 0;
                int sample;

                i2sCounter++;

                /* Provide samples from the SRC output FIFO */
                for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_OUT; i++)
                {
                    error |= fifo_pop(fifo_play, srcOutputBuff_play, sample);

                    /* Send a 0 zero on FIFO error e.g. underflow */
                    if(error)
                        samples[i] = 0;
                    else
                        samples[i] = sample;
                }
                if(error)
                {
                    init_fifo(fifo_play, srcOutputBuff_play, sizeof(srcOutputBuff_play)/sizeof(srcOutputBuff_play[0]));
                }
                break;
            }
        }
    }
}

void src_task(streaming chanend c, int instance, int inputFsCode, int outputFsCode)
{
    int inputBuff[SRC_N_IN_SAMPLES * SRC_CHANNELS_PER_INSTANCE];
    int outputBuff[SRC_OUT_BUFF_SIZE];
    int sampsOut = 0;

    memset(inputBuff, 0, sizeof(inputBuff));
    memset(outputBuff, 0, sizeof(outputBuff));

#if USE_ASRC
    asrc_state_t sASRCState[SRC_CHANNELS_PER_INSTANCE];                                   // ASRC state machine state
    int iASRCStack[SRC_CHANNELS_PER_INSTANCE][ASRC_STACK_LENGTH_MULT * SRC_N_IN_SAMPLES * 100]; // Buffer between filter stages
    asrc_ctrl_t sASRCCtrl[SRC_CHANNELS_PER_INSTANCE];                                     // Control structure
    asrc_adfir_coefs_t asrc_adfir_coefs;                                                  // Adaptive filter coefficients
    uint64_t fsRatio;

    for(int ui = 0; ui < SRC_CHANNELS_PER_INSTANCE; ui++)
    {
        unsafe
        {
            // Set state, stack and coefs into ctrl structure
            sASRCCtrl[ui].psState                   = &sASRCState[ui];
            sASRCCtrl[ui].piStack                   = iASRCStack[ui];
            sASRCCtrl[ui].piADCoefs                 = asrc_adfir_coefs.iASRCADFIRCoefs;
        }
    }

    fsRatio = asrc_init(inputFsCode, outputFsCode, sASRCCtrl, SRC_CHANNELS_PER_INSTANCE, SRC_N_IN_SAMPLES, SRC_DITHER_SETTING);
#else
    ssrc_state_t sSSRCState[SRC_CHANNELS_PER_INSTANCE];                                     // State of SSRC module
    int iSSRCStack[SRC_CHANNELS_PER_INSTANCE][SSRC_STACK_LENGTH_MULT * SRC_N_IN_SAMPLES];   // Buffers between processing stages
    ssrc_ctrl_t sSSRCCtrl[SRC_CHANNELS_PER_INSTANCE];                                       // SSRC Control structure

    /* Set state, stack and coefs into ctrl structures */
    for(int ui = 0; ui < SRC_CHANNELS_PER_INSTANCE; ui++)
    {
        unsafe
        {
            sSSRCCtrl[ui].psState                   = &sSSRCState[ui];
            sSSRCCtrl[ui].piStack                   = iSSRCStack[ui];
        }
    }

    ssrc_init(inputFsCode, outputFsCode, sSSRCCtrl, SRC_CHANNELS_PER_INSTANCE, SRC_N_IN_SAMPLES, SRC_DITHER_SETTING);
#endif

    while(1)
    {
        uint64_t fsRatio_;

        c :> fsRatio_;

#pragma loop unroll
        /* Receive samples to process */
        for(int i=0; i<SRC_N_IN_SAMPLES * SRC_CHANNELS_PER_INSTANCE; i++)
        {
            c :> inputBuff[i];
        }

        /* Send out the number of samples we have to output */
        c <: sampsOut;

        /* Send output samples */
#pragma loop unroll
        for(int i = 0; i < sampsOut * SRC_CHANNELS_PER_INSTANCE; i++)
        {
            c <: outputBuff[i];
        }

        /* Process input buffer into output buffer */
#if USE_ASRC
        sampsOut = asrc_process(inputBuff, outputBuff, fsRatio_, sASRCCtrl);
#else
        sampsOut = ssrc_process(inputBuff, outputBuff, sSSRCCtrl);
#endif

    }
}

void i2s_driver(chanend c)
{
    interface i2s_frame_callback_if i_i2s;
    streaming chan c_src_play[SRC_N_INSTANCES];
    streaming chan c_src_rec[SRC_N_INSTANCES];

    set_port_clock(p_off_bclk, clk_bclk);

    par
    {
        i2s_frame_slave(i_i2s, p_i2s_dout, 1, p_i2s_din, sizeof(p_i2s_din)/sizeof(p_i2s_din[0]), DATA_BITS, p_i2s_bclk, p_i2s_lrclk, clk_bclk);

        i2s_data(i_i2s, c, c_src_play, c_src_rec);

        /* Playback SRC tasks */
        par (int i=0; i < SRC_N_INSTANCES; i++)
        {
            src_task(c_src_play[i], i, FS_CODE_96, FS_CODE_48);
        }

         /* Record SRC tasks */
        par (int i=0; i < SRC_N_INSTANCES; i++)
        {
            src_task(c_src_rec[i], i, FS_CODE_48, FS_CODE_96);
        }
    }
}
