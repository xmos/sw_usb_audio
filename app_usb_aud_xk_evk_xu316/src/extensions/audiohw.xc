// Copyright 2021-2026 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#include "xua.h"
#include "xk_evk_xu316/board.h"


#if !(DEFAULT_FREQ >= 22050)
#error
#endif

static const xk_evk_xu316_config_t config = {

    0 /* fixed mclk using the app PLL generated in lib_xua*/
};


void AudioHwRemote(chanend c)
{
    xk_evk_xu316_AudioHwRemote(c);
}

/* Note this is called from tile[1] but the I2C lines to the CODEC are on tile[0]
 * use a channel to communicate CODEC reg read/writes to a remote core */
void AudioHwInit()
{
    xk_evk_xu316_AudioHwInit(config);
}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    xk_evk_xu316_AudioHwConfig(samFreq, 0, dsdMode, sampRes_DAC, sampRes_ADC);
}

