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


unsafe client interface i2c_master_if i_i2c_client;

/* Note this is called from tile[1] but the I2C lines to the CODEC are on tile[0].
 * The i2c_master_if connection spans the two tiles. */
void AudioHwInit()
{
    unsafe
    {
        /* Wait until global is set */
        while(!(unsigned) i_i2c_client);
        xk_evk_xu316_AudioHwInit((client interface i2c_master_if)i_i2c_client, config);
    }
}

/* Configures the external audio hardware for the required sample frequency. */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    unsafe
    {
        xk_evk_xu316_AudioHwConfig((client interface i2c_master_if)i_i2c_client,
                                   samFreq, 0, dsdMode, sampRes_DAC, sampRes_ADC);
    }
}
