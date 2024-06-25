#include "xua.h"
#include <xk_audio_316_mc_ab/board.h>

#if (XUA_PCM_FORMAT == XUA_PCM_FORMAT_TDM) && (XUA_I2S_N_BITS != 32)
#warning ADC only supports TDM operation at 32 bits
#endif


#if (XUA_PCM_FORMAT == XUA_PCM_FORMAT_TDM) && (XUA_I2S_N_BITS != 32)
#warning ADC only supports TDM operation at 32 bits
#endif

/* TODO this is a key frequency and should be moved into lib_xua */
#if (XUA_SYNCMODE == XUA_SYNCMODE_SYNC)
    #define PLL_SYNC_FREQ           (500)
#else
    #if (XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN)
    /* Choose a frequency the xcore can easily generate internally */
    #define PLL_SYNC_FREQ           (300)
    #else
    #define PLL_SYNC_FREQ           (1000000)
    #endif
#endif

static xk_audio_316_mc_ab_config_t config = {
    // clk_mode
    (XUA_SYNCMODE == XUA_SYNCMODE_SYNC || XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN)
    ? ( XUA_USE_SW_PLL
        ? CLK_PLL : CLK_CS2100 )
    : CLK_FIXED,
    
    // dac_is_clk_master
    CODEC_MASTER,
    
    // default_mclk
    (DEFAULT_FREQ % 22050 == 0) ? MCLK_441 : MCLK_48,

    // pll_sync_freq
    PLL_SYNC_FREQ,

    // pcm_format
    XUA_PCM_FORMAT,

    // i2s_n_bits
    XUA_I2S_N_BITS,

    // i2s_chans_per_frame
    I2S_CHANS_PER_FRAME
};

unsafe client interface i2c_master_if i_i2c_client;

/* Board setup for XU316 MC Audio (1v1) */
void board_setup()
{
    xk_audio_316_mc_ab_board_setup(config);
}

/* Configures the external audio hardware at startup */
void AudioHwInit()
{
    unsafe{ 
        /* Wait until global is set */
        while(!(unsigned) i_i2c_client);
        xk_audio_316_mc_ab_AudioHwInit((client interface i2c_master_if)i_i2c_client, config); 
    }
}

/* Configures the external audio hardware for the required sample frequency */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    unsafe {xk_audio_316_mc_ab_AudioHwConfig((client interface i2c_master_if)i_i2c_client, config, samFreq, mClk, dsdMode, sampRes_DAC, sampRes_ADC);}
}

