/*
 * audio_process.h
 *
 *  Created on: 11 Jan 2016
 *      Author: johne2
 */


#ifndef AUDIO_PROCESS_H_
#define AUDIO_PROCESS_H_

//#include "control.h"

// Voice Library / DSP Framework Module IDs
#define IVL_BASE_MODULE_ID      0x4000
#define IVL_INIT_MODULE_ID      0x4100
#define IVL_BYPASS_MODULE_ID    0x4200
#define IVL_MIC_MODULE_ID       0x4300
#define IVL_BEAM_MODULE_ID      0x4400
#define IVL_NOISE_MODULE_ID     0x4500
#define IVL_DEREV_MODULE_ID     0x4600
#define IVL_AEC_MODULE_ID       0x4700
#define IVL_AGC_MODULE_ID       0x4800
#define IVL_EQ_MODULE_ID        0x4900
#define IVL_SPK_LIM_MODULE_ID   0x4A00
#define IVL_SPK_CMP_MODULE_ID   0x4B00
#define IVL_DIAG_MODULE_ID      0x4C00

#define LMA_DOA_MODULE_ID       0x6000
#define LMA_DOA_BASIC_SETTING   0x6100
#define LMA_DOA_VAD_THRESHOLD   0x6200



// Voice Library Parameter Limits
#define MIC_GAIN_MIN            -100
#define MIC_GAIN_MAX            36
#define MIC_GAIN_INI            0

#define SPK_GAIN_MIN            100
#define SPK_GAIN_MAX            100
#define SPK_GAIN_INI            0

#define BYPASS_ON_MIN           0
#define BYPASS_ON_MAX           4
#define BYPASS_ON_INI           0

#define MIC_SHIFT_MIN           0
#define MIC_SHIFT_MAX           4
#define MIC_SHIFT_INI           0

#define BF_DIRECTION_MIN        0
#define BF_DIRECTION_MAX        3
#define BF_DIRECTION_INI        1

#define BF_FOCUS_MIN            0
#define BF_FOCUS_MAX            10
#define BF_FOCUS_INI            5

#define BF_DIFF_GAIN_MIN        -20
#define BF_DIFF_GAIN_MAX        0
#define BF_DIFF_GAIN_INI        -8

#define NS_ATTEN_MIN            -20
#define NS_ATTEN_MAX            0
#define NS_ATTEN_INI            -12

#define RVB_ATTEN_MIN           -20
#define RVB_ATTEN_MAX           0
#define RVB_ATTEN_INI           -12

#define AEC_DELAY_MIN           -1
#define AEC_DELAY_MAX           30
#define AEC_DELAY_INI           -1

#define AEC_STRENGTH_MIN        0
#define AEC_STRENGTH_MAX        10
#define AEC_STRENGTH_INI        0

#define AEC_NONLIN_MIN          0
#define AEC_NONLIN_MAX          10
#define AEC_NONLIN_INI          0

#define AEC_LECHOFF_MIN         -80
#define AEC_LECHOFF_MAX         0
#define AEC_LECHOFF_INI         -24

#define AEC_LECHTIME_MIN        0
#define AEC_LECHTIME_MAX        400
#define AEC_LECHTIME_INI        200

#define AEC_FTHR_MIN            -80
#define AEC_FTHR_MAX            0
#define AEC_FTHR_INI            -18

#define AEC_NTHR_MIN            0
#define AEC_NTHR_MAX            40
#define AEC_NTHR_INI            15

#define AEC_DTTHR_MIN           0
#define AEC_DTTHR_MAX           40
#define AEC_DTTHR_INI           12

#define AEC_DTREL_MIN           0
#define AEC_DTREL_MAX           24
#define AEC_DTREL_INI           10

#define AEC_DTATT_MIN           -80
#define AEC_DTATT_MAX           0
#define AEC_DTATT_INI           -30

#define AEC_IGAIN_MIN           -60
#define AEC_IGAIN_MAX           20
#define AEC_IGAIN_INI           0

#define AGC_IGAIN_MIN           0
#define AGC_IGAIN_MAX           36
#define AGC_IGAIN_INI           18

#define AGC_TGAIN_MIN           -30
#define AGC_TGAIN_MAX           -10
#define AGC_TGAIN_INI           -16

#define MIC_EQ_INDEX_MIN        0
#define MIC_EQ_INDEX_MAX        2
#define MIC_EQ_INDEX_INI        0

#define SPK_EQ_INDEX_MIN        0
#define SPK_EQ_INDEX_MAX        2
#define SPK_EQ_INDEX_INI        0

#define SPK_LIM_THR_MIN         -20
#define SPK_LIM_THR_MAX         0
#define SPK_LIM_THR_INI         -3

#define SPK_COMP_THR_MIN        -30
#define SPK_COMP_THR_MAX        0
#define SPK_COMP_THR_INI        -18

#define SPK_COMP_GAIN_MIN       0
#define SPK_COMP_GAIN_MAX       12
#define SPK_COMP_GAIN_INI       8

#define SPK_COMP_RATIO_MIN      0
#define SPK_COMP_RATIO_MAX      9
#define SPK_COMP_RATIO_INI      3


//void audio_process(client il_callback_if i_il,
//    server interface control_if i_control);

//int cntrlAudioProcess(int argc, int argv[IVL_MAX_NUM_MODULE_ARGS]);

#endif /* AUDIO_PROCESS_H_ */
