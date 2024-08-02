#include "xua.h"

#include "app_usb_aud_xk_216_mc.h"
#include <xk_audio_216_mc_ab/board.h>

#if (XUA_SYNCMODE == XUA_SYNCMODE_SYNC)
    #define CLK_MODE AUD_216_CLK_EXTERNAL_PLL_USB
    #define PLL_SYNC_FREQ           (500)
#elif (XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN)
    #define CLK_MODE AUD_216_CLK_EXTERNAL_PLL
    /* Choose a frequency the xcore can easily generate internally */
    #define PLL_SYNC_FREQ           (300)
#else
    #define CLK_MODE AUD_216_CLK_FIXED
    #define PLL_SYNC_FREQ           (1000000)
#endif

static const xk_audio_216_mc_ab_config_t config = {
    // clk_mode
    CLK_MODE,

    // codec_is_clk_master
    CODEC_MASTER,

    // usb_sel
    (USB_SEL_A ? AUD_216_USB_A : AUD_216_USB_B),

    // pcm_format
    XUA_PCM_FORMAT,

    // pll_sync_freq
    PLL_SYNC_FREQ
};

void AudioHwInit()
{
    xk_audio_216_mc_ab_AudioHwInit(config);
}

void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    
    xk_audio_216_mc_ab_AudioHwConfig(config, samFreq, mClk, dsdMode, sampRes_DAC, sampRes_ADC);

}
