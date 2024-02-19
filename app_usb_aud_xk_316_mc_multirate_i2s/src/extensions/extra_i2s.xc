#include <platform.h>
#include <xs1.h>
#include <print.h>
#include <stdlib.h>
#include <string.h>
#include "i2s.h"
#include "src.h"
#include "xua.h"
#include "asynchronous_fifo.h"
#include "asrc_timestamp_interpolation.h"
#include <xscope.h>

/* TODO
    - Seperate recording and playback SRC related defines
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

void exit(int);

unsafe chanend uc_i2s;

/* Note, re-using I2S data lines on MC audio board for LR and Bit clocks */
#if (EXTRA_I2S_CHAN_COUNT_OUT > 0)
on tile[1]: out buffered port:32 p_i2s_dout[1] = {PORT_I2S_DAC1};
#else
#define p_i2s_dout null
#endif

#if (EXTRA_I2S_CHAN_COUNT_IN > 0)
on tile[1]: in buffered port:32 p_i2s_din[1] =   {PORT_SPDIF_OUT};
#else
#define p_i2s_din null
#endif

on tile[1]: in port p_i2s_bclk =                 PORT_I2S_DAC2;
on tile[1]: in buffered port:32 p_i2s_lrclk =    PORT_I2S_DAC3;
on tile[1]: in port p_off_bclk =                 XS1_PORT_16A;
on tile[1]: clock clk_bclk =                     XS1_CLKBLK_1;

extern in port p_mclk_in;

/* TODO all these defines are shared between playback and record streams - this should be fixed */

#define     SRC_N_CHANNELS                (2)   // Total number of audio channels to be processed by SRC (minimum 1)
#define     SRC_N_INSTANCES               (2)   // Number of instances (each usually run a logical core) used to process audio (minimum 1)
#define     SRC_CHANNELS_PER_INSTANCE     (SRC_N_CHANNELS/SRC_N_INSTANCES) // Calculated number of audio channels processed by each core
#define     SRC_N_IN_SAMPLES              (4)   // Number of samples per channel in each block passed into SRC each call
                                                // Must be a power of 2 and minimum value is 4 (due to two /2 decimation stages)
#define     SRC_N_OUT_IN_RATIO_MAX        (5)   // Max ratio between samples out:in per processing step (44.1->192 is worst case)
#define     SRC_DITHER_SETTING            (0)   // Enables or disables quantisation of output with dithering to 24b
#define     SRC_MAX_NUM_SAMPS_OUT         (SRC_N_OUT_IN_RATIO_MAX * SRC_N_IN_SAMPLES)
#define     SRC_OUT_BUFF_SIZE             (SRC_CHANNELS_PER_INSTANCE * SRC_MAX_NUM_SAMPS_OUT) // Size of output buffer for SRC for each instance
#define     SRC_OUT_FIFO_SIZE             (SRC_N_CHANNELS * SRC_MAX_NUM_SAMPS_OUT * 4)        // Size of output FIFO for SRC

/* Stuff that must be defined for lib_src */
#define SSRC_N_IN_SAMPLES                 (SRC_N_IN_SAMPLES) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_ssrc.h */
#define ASRC_N_IN_SAMPLES                 (SRC_N_IN_SAMPLES) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_asrc.h */

#define SSRC_N_CHANNELS                   (SRC_CHANNELS_PER_INSTANCE) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_ssrc.h */
#define ASRC_N_CHANNELS                   (SRC_CHANNELS_PER_INSTANCE) /* Used by SRC_STACK_LENGTH_MULT in src_mrhf_asrc.h */

/* Current rate of USB input/output */
int g_usbSamFreq = DEFAULT_FREQ;

unsafe
{
    int * unsafe g_usbSamFreqPtr = &g_usbSamFreq;
}

void UserBufferManagementInit(unsigned samFreq)
{
    /* Check for sample-rate change */
    if(g_usbSamFreq != samFreq)
    {
        g_usbSamFreq = samFreq;

        unsafe
        {
            outuchar((chanend) uc_i2s, 1);
            outuint((chanend) uc_i2s, g_usbSamFreq);
            outct((chanend) uc_i2s, XS1_CT_END);

            /* Wait for handshake */
            chkct((chanend) uc_i2s, XS1_CT_END);
        }
    }
}

#pragma unsafe arrays
void UserBufferManagement(unsigned sampsFromUsbToAudio[], unsigned sampsFromAudioToUsb[])
{
    unsafe
    {
        outuchar((chanend) uc_i2s, 0);
#pragma loop unroll
        for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_OUT; i++)
        {
            outuint((chanend)uc_i2s, sampsFromUsbToAudio[i + EXTRA_I2S_CHAN_INDEX_OUT]);
        }
        outct((chanend)uc_i2s, XS1_CT_END);

#pragma loop unroll
        for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
        {
            sampsFromAudioToUsb[i + EXTRA_I2S_CHAN_INDEX_IN] = inuint((chanend) uc_i2s);
        }
        chkct((chanend)uc_i2s, XS1_CT_END);
    }
}

#pragma unsafe arrays
static inline uint64_t trigger_src(streaming chanend c_src[SRC_N_INSTANCES],
                                int srcInputBuff[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE],
                                uint64_t fsRatio, asynchronous_fifo_t * unsafe a, int32_t now, int xscope_used, int idealFsRatio)
{
    int32_t error = 0;
    int nSamps = 0;
    int32_t timestamp;
    int32_t samples[SRC_CHANNELS_PER_INSTANCE*SRC_N_CHANNELS * SRC_MAX_NUM_SAMPS_OUT];
#pragma loop unroll
    for (int i=0; i<SRC_N_INSTANCES; i++)
    {
        c_src[i] <: (uint64_t) fsRatio;

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
        c_src[i] :> timestamp;
        c_src[i] <: now;
    }

    int chanIdx = 0;
    for (int j=0; j < nSamps; j++)
    {
#pragma loop unroll
        for (int k=0; k<SRC_CHANNELS_PER_INSTANCE; k++)
        {
            int32_t sample;
#pragma loop unroll
            for (int i=0; i<SRC_N_INSTANCES; i++)
            {
                c_src[i] :> sample;
                samples[chanIdx++] = sample;
            }
        }
    }

    error = asynchronous_fifo_producer_put(a, samples, nSamps, timestamp, xscope_used);

    /* Produce fsRatio from error */
    fsRatio = (((int64_t)idealFsRatio) << 32) + (error * (int64_t) idealFsRatio);

    return fsRatio;
}

#ifndef LOG_CONTROLLER_REC
#define LOG_CONTROLLER_REC (0)
#endif

#ifndef LOG_CONTROLLER_PLAY
#define LOG_CONTROLLER_PLAY (0)
#endif

#define CONT_LOG_DELAY     (0)
#define CONT_LOG_SIZE      (18000)
#define CONT_LOG_SUBSAMPLE (128)

#if LOG_CONTROLLER_REC
uint64_t r_r[CONT_LOG_SIZE];
int logCounterRec = 0;
int logCounterSubRec = 0;
#endif

#if LOG_CONTROLLER_PLAY
uint64_t r_p[CONT_LOG_SIZE];
int logCounterPlay = 0;
int logCounterSubPlay = 0;
#endif


[[distributable]]
void i2s_data(server i2s_frame_callback_if i_i2s,
    streaming chanend c_src_rec[SRC_N_INSTANCES],
    asynchronous_fifo_t * unsafe async_fifo_state_play,
    asynchronous_fifo_t * unsafe async_fifo_state_rec)
{
    int sampleIdx_rec = 0;
    int samFreq;
    unsafe
    {
        samFreq = *g_usbSamFreqPtr;
    }
    int newSamFreq = samFreq;

    float floatRatio_rec = (float) SAMPLE_FREQUENCY/(float)samFreq;
    uint64_t fsRatio_rec = (uint64_t) (floatRatio_rec * (1LL << 60));
    int idealFsRatio_rec = (fsRatio_rec + (1<<31)) >> 32;

    int srcInputBuff_rec[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE];
#if LOG_CONTROLLER_REC
    int logCounterDelay = 0;
    int logCounterGo = 0;
#endif
    int32_t now;
    timer t;

    while(1)
    {
        select
        {
            case i_i2s.init(i2s_config_t &?i2s_config, tdm_config_t &?tdm_config):
                i2s_config.mode = I2S_MODE_I2S;

                floatRatio_rec = (float) SAMPLE_FREQUENCY/(float)samFreq;
                fsRatio_rec = (uint64_t) (floatRatio_rec * (1LL << 60));
                idealFsRatio_rec = (fsRatio_rec + (1<<31)) >> 32;

                asynchronous_fifo_reset_producer(async_fifo_state_rec);
                asynchronous_fifo_init_PID_fs_codes(async_fifo_state_rec, sr_to_fscode(SAMPLE_FREQUENCY), sr_to_fscode(samFreq));

                for(int i=0; i < SRC_N_INSTANCES; i++)
                unsafe
                {
                    soutct(c_src_rec[i], XS1_CT_END);
                    c_src_rec[i] <: (int)FS_CODE_48;
                    c_src_rec[i] <: (int)sr_to_fscode(samFreq);
                    schkct(c_src_rec[i], XS1_CT_END);
                }
                break;

            /* Inform the I2S slave whether it should restart or exit */
            case i_i2s.restart_check() -> i2s_restart_t restart:

                /* Check for SR Change */
                unsafe
                {
                    newSamFreq = *g_usbSamFreqPtr;
                }
                if(samFreq != newSamFreq)
                    restart = I2S_RESTART;
                else
                    restart = I2S_NO_RESTART;
                break;

            case i_i2s.receive(size_t num_in, int32_t samples[num_in]):

                t :> now;

#if (EXTRA_I2S_CHAN_COUNT_IN > 0)

                for(size_t i = 0; i < EXTRA_I2S_CHAN_COUNT_IN; i++)
                {
                    srcInputBuff_rec[i/SRC_CHANNELS_PER_INSTANCE][sampleIdx_rec][i % SRC_CHANNELS_PER_INSTANCE] = samples[i];
                }

                /* Add to recording path ASRC input buffer */
                sampleIdx_rec++;

                if(sampleIdx_rec == SRC_N_IN_SAMPLES)
                {
                    sampleIdx_rec = 0;

#if LOG_CONTROLLER_REC
                        logCounterDelay ++;

                        if(logCounterDelay > CONT_LOG_DELAY)
                            logCounterGo = 1;

                        if(logCounterGo)
                            logCounterSubRec++;


                        if(logCounterSubRec == CONT_LOG_SUBSAMPLE)
                        unsafe{
                            logCounterSubRec = 0;
                            r_r[logCounterRec] = fsRatio_rec;
                            ns_r[logCounterRec] = nsamps;

                            logCounterRec++;

                            if(logCounterRec >= CONT_LOG_SIZE)
                            {
                                for(int i = 0; i < CONT_LOG_SIZE; i++)
                                {
                                    float ratio = (float) r_r[i] / (float) (1LL<<60);
                                    printf("%d %f\n", ns_r[i], ratio);
                                }
                                exit(1);
                            }
                        }
#endif
                    /* Trigger_src for record path */
                    fsRatio_rec = trigger_src(c_src_rec, srcInputBuff_rec, fsRatio_rec, async_fifo_state_rec, now, 0, idealFsRatio_rec);
                }
#endif
                break;

            case i_i2s.send(size_t num_out, int32_t samples[num_out]):

#if (EXTRA_I2S_CHAN_COUNT_OUT > 0)
                int32_t playSamples[EXTRA_I2S_CHAN_COUNT_OUT];

                asynchronous_fifo_consumer_get(async_fifo_state_play, playSamples, now);

                for(int i = 0; i < num_out; i++)
                {
                    samples[i] = playSamples[i];
                }
#endif
                break;
        }
    }
}

#define FIFO_LENGTH (100)
int64_t array[ASYNCHRONOUS_FIFO_INT64_ELEMENTS(FIFO_LENGTH, 2)];
int64_t array_rec[ASYNCHRONOUS_FIFO_INT64_ELEMENTS(FIFO_LENGTH, 2)];

#pragma unsafe arrays
int src_manager(chanend c_usb,
    streaming chanend c_src_play[SRC_N_INSTANCES],
    int samFreq, int startUp,
    asynchronous_fifo_t * unsafe async_fifo_state_play,
    asynchronous_fifo_t * unsafe async_fifo_state_rec)
{

    unsigned char srChange;

    int srcInputBuff_play[SRC_N_INSTANCES][SRC_N_IN_SAMPLES][SRC_CHANNELS_PER_INSTANCE];
    int32_t srcOutputBuff_rec[EXTRA_I2S_CHAN_COUNT_IN];
    int sampleIdx_play = 0;
    float floatRatio_play = (float) samFreq/(float) SAMPLE_FREQUENCY;
    /* Q60 representations of the above */
    uint64_t fsRatio_play = (uint64_t) (floatRatio_play * (1LL << 60));
    int idealFsRatio_play = (fsRatio_play + (1<<31)) >> 32;
    timer t;

#if LOG_CONTROLLER_PLAY
    int logCounterDelay = 0;
    int logCounterGo = 0;
#endif
    if(!startUp)
        /* Handshsake that we are ready to go after SR change */
        /* OR inital request for usb data */
        outct(c_usb, XS1_CT_END);

    while (1)
    {
        select
        {
            case inuchar_byref(c_usb, srChange):

                if(srChange)
                {
                    samFreq = inuint(c_usb);
                    inct(c_usb);

                    /* Return new sample frequency we need to switch to */
                    return samFreq;
                }
                else
                {
                    unsigned now;
                    t :> now;

                    /* Receive samples from USB audio (other side of the UserBufferManagement() comms) */
#pragma loop unroll
                    for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_OUT; i++)
                    {
                        srcInputBuff_play[i/SRC_CHANNELS_PER_INSTANCE][sampleIdx_play][i % SRC_CHANNELS_PER_INSTANCE] = inuint(c_usb);
                    }
                    chkct(c_usb, XS1_CT_END);

                    asynchronous_fifo_consumer_get(async_fifo_state_rec, srcOutputBuff_rec, now);

                    /* Send samples to USB audio (other side of the UserBufferManagement() comms */
#pragma loop unroll
                    for(size_t i = 0; i< EXTRA_I2S_CHAN_COUNT_IN; i++)
                    {
                        outuint(c_usb, srcOutputBuff_rec[i]);
                    }
                    outct(c_usb, XS1_CT_END);

                    sampleIdx_play++;

                    if(sampleIdx_play == SRC_N_IN_SAMPLES)
                    {
                        sampleIdx_play = 0;
#if LOG_CONTROLLER_PLAY
                        logCounterDelay ++;

                        if(logCounterGo)
                            logCounterSubPlay++;
                        if(logCounterDelay > CONT_LOG_DELAY)
                             logCounterGo = 1;

                        if(logCounterSubPlay == CONT_LOG_SUBSAMPLE)
                        unsafe{
                            logCounterSubPlay = 0;
                            int fillPlay = (async_fifo_state_play->write_ptr - async_fifo_state_play->read_ptr + async_fifo_state_play->max_fifo_depth)
                                % async_fifo_state_play->max_fifo_depth;
                            r_p[logCounterPlay] = fsRatio_play;

                            logCounterPlay++;

                            if(logCounterPlay >= CONT_LOG_SIZE)
                            {
                                if(logCounterGo)
                                {
                                    for(int i = 0; i < CONT_LOG_SIZE; i++)
                                    {
                                        float ratio = (float) r_p[i] / (float) (1LL<<60);
                                        printf("%f\n", ratio);
                                    }
                                    exit(1);
                                }
                                else
                                    logCounterPlay = 0;
                            }
                        }
#endif

#if (EXTRA_I2S_CHAN_COUNT_OUT > 0)
                        /* Send samples to SRC tasks. This function adds returned sample to FIFO */
                        fsRatio_play = trigger_src(c_src_play, srcInputBuff_play, fsRatio_play, async_fifo_state_play, now, 0, idealFsRatio_play);
#endif
                    }
                }
                break;

        }
    }

__builtin_unreachable();
    /* Should never get here */
    return 0;
}

static int interpolation_ticks_2D[6][6] =
{
    {  2268, 2268, 2268, 2268, 2268, 2268},
    {  2083, 2083, 2083, 2083, 2083, 2083},
    {  2268, 2268, 1134, 1134, 1134, 1134},
    {  2083, 2083, 1042, 1042, 1042, 1042},
    {  2268, 2268, 1134, 1134,  567,  567},
    {  2083, 2083, 1042, 1042,  521,  521}
};

void src_task_(streaming chanend c, int instance, int inputFsCode, int outputFsCode)
{
    int inputBuff[SRC_N_IN_SAMPLES * SRC_CHANNELS_PER_INSTANCE];
    int outputBuff[SRC_OUT_BUFF_SIZE];
    int sampsOut = 0;

    int interpolation_ticks = interpolation_ticks_2D[inputFsCode][outputFsCode];

    memset(inputBuff, 0, sizeof(inputBuff));
    memset(outputBuff, 0, sizeof(outputBuff));

#if USE_ASRC
    asrc_state_t sASRCState[SRC_CHANNELS_PER_INSTANCE];                                   // ASRC state machine state
    int iASRCStack[SRC_CHANNELS_PER_INSTANCE][ASRC_STACK_LENGTH_MULT * SRC_N_IN_SAMPLES]; // Buffer between filter stages
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

    int32_t tsIn = 0, tsOut = 0;

    while(1)
    {
        uint64_t fsRatio_;

        /* Check for exit */
        if(stestct(c))
        {
            sinct(c);
            c :> inputFsCode;
            c :> outputFsCode;

            interpolation_ticks = interpolation_ticks_2D[inputFsCode][outputFsCode];

            fsRatio = asrc_init(inputFsCode, outputFsCode, sASRCCtrl, SRC_CHANNELS_PER_INSTANCE, SRC_N_IN_SAMPLES, SRC_DITHER_SETTING);

            /* Handshake back when init complete */
            soutct(c, XS1_CT_END);
            continue;
        }

        c :> fsRatio_;

#pragma loop unroll
        /* Receive samples to process */
        for(int i=0; i<SRC_N_IN_SAMPLES * SRC_CHANNELS_PER_INSTANCE; i++)
        {
            c :> inputBuff[i];
        }

        /* Send out the number of samples we have to output */
        c <: sampsOut;

        /* Send out the output timestamp */
        c <: tsOut;
        c :> tsIn;

        /* Send output samples */
#pragma loop unroll
        for(int i = 0; i < sampsOut * SRC_CHANNELS_PER_INSTANCE; i++)
        {
            c <: outputBuff[i];
        }

        /* Process input buffer into output buffer */
#if USE_ASRC
        sampsOut = asrc_process(inputBuff, outputBuff, fsRatio_, sASRCCtrl);
        if(sampsOut)
        unsafe
        {
            tsOut = asrc_timestamp_interpolation(tsIn, &sASRCCtrl[0], interpolation_ticks);
        }
#else
        sampsOut = ssrc_process(inputBuff, outputBuff, sSSRCCtrl);
#endif
    }
}

void i2s_driver(chanend c_usb)
{
    interface i2s_frame_callback_if i_i2s;
    streaming chan c_src_play[SRC_N_INSTANCES];
    streaming chan c_src_rec[SRC_N_INSTANCES];

    set_port_clock(p_off_bclk, clk_bclk);

    int usbSr = DEFAULT_FREQ;
    int startUp = 1;

    unsafe
    {
        asynchronous_fifo_t * unsafe async_fifo_state_play = (asynchronous_fifo_t *)array;
        asynchronous_fifo_t * unsafe async_fifo_state_rec = (asynchronous_fifo_t *)array_rec;

        asynchronous_fifo_init(async_fifo_state_play, 2, FIFO_LENGTH);
        asynchronous_fifo_init(async_fifo_state_rec, 2, FIFO_LENGTH);

        asynchronous_fifo_init_PID_fs_codes(async_fifo_state_play, sr_to_fscode(usbSr), sr_to_fscode(SAMPLE_FREQUENCY));
        asynchronous_fifo_init_PID_fs_codes(async_fifo_state_rec, sr_to_fscode(SAMPLE_FREQUENCY), sr_to_fscode(usbSr));

        par
        {
            par
            {
                [[distribute]]i2s_data(i_i2s, c_src_rec, async_fifo_state_play, async_fifo_state_rec);
                i2s_frame_slave(i_i2s, p_i2s_dout, (EXTRA_I2S_CHAN_COUNT_OUT/2), p_i2s_din, (EXTRA_I2S_CHAN_COUNT_IN/2), DATA_BITS, p_i2s_bclk, p_i2s_lrclk, clk_bclk);
            }
            while(1)
            {

                /* This task produces into fifo for play and consumes from fifo for record */
                usbSr = src_manager(c_usb, c_src_play, usbSr, startUp, async_fifo_state_play, async_fifo_state_rec);
                startUp = 0;

                unsafe
                {
                    *g_usbSamFreqPtr = usbSr;
                }

#if(EXTRA_I2S_CHAN_COUNT_OUT > 0)
                asynchronous_fifo_reset_producer(async_fifo_state_play);
                asynchronous_fifo_init_PID_fs_codes(async_fifo_state_play, sr_to_fscode(usbSr), sr_to_fscode(SAMPLE_FREQUENCY));

                for(int i=0; i < SRC_N_INSTANCES; i++)
                    unsafe
                    {
                        soutct(c_src_play[i], XS1_CT_END);
                        c_src_play[i] <: (int)sr_to_fscode(usbSr);
                        c_src_play[i] <: (int)FS_CODE_48;
                        schkct(c_src_play[i], XS1_CT_END);
                    }
#endif
            }

#if(EXTRA_I2S_CHAN_COUNT_OUT > 0)
            /* Playback SRC tasks */
            par (int i=0; i < SRC_N_INSTANCES; i++)
            {
                unsafe
                {
                    src_task_(c_src_play[i], i, sr_to_fscode(DEFAULT_FREQ), FS_CODE_48);
                }
            }
#endif
#if(EXTRA_I2S_CHAN_COUNT_IN > 0)
            /* Record SRC tasks */
            par (int i = SRC_N_INSTANCES ; i < 2*SRC_N_INSTANCES; i++)
            {
                unsafe
                {
                    src_task_(c_src_rec[i-SRC_N_INSTANCES], i, FS_CODE_48, sr_to_fscode(DEFAULT_FREQ));
                }
            }
#endif
        } /* par */
    } /* unsafe */
}
