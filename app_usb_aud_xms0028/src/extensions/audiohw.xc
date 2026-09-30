// Copyright 2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include "xua.h"
#include <xms0028/board.h>

unsafe client interface i2c_master_if i_i2c_client;

static const xms0028_config_t config = {
    (DEFAULT_FREQ % 22050 == 0) ? MCLK_441 : MCLK_48,
    XMS0028_INPUT_LINE_IN
};

/* Configures the external audio hardware at startup. */
void AudioHwInit()
{
    unsafe {
        while (!(unsigned) i_i2c_client) {
        }

        xms0028_AudioHwInit(
            (client interface i2c_master_if) i_i2c_client, config);
    }
}

/* Configures the external audio hardware for the required sample frequency.
 *
 * samFreq: Sample frequency in Hz
 * mClk: Master clock frequency in Hz
 * dsdMode: DSD mode flag (0 for PCM, non-zero for DSD)
 * sampRes_DAC: Sample resolution for DAC in bits
 * sampRes_ADC: Sample resolution for ADC in bits
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode,
                   unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    unsafe {
        xms0028_AudioHwConfig(
            (client interface i2c_master_if) i_i2c_client,
            samFreq,
            mClk,
            dsdMode,
            sampRes_DAC,
            sampRes_ADC);
    }
}
