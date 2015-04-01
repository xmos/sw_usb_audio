#include <xs1.h>
#include <assert.h>
#include "devicedefines.h"
#include <platform.h>
#include "gpio.h"
#include "cs4384.h"
#include "cs5368.h"
#include "cs2100.h"
#include "print.h"
#include "dsd_support.h"

/* I2C bus to DAC */
on tile[AUDIO_IO_TILE]: struct r_i2c r_i2c_aud = { PORT_I2C_SCL_AUD, PORT_I2C_SDA_AUD };

on tile[AUDIO_IO_TILE]: port p_adrst_cksel_dsd = PORT_CODEC_RST_CLKSEL_DSD;
on tile[AUDIO_IO_TILE]: port p_pwr_pll_mute = PORT_PWR_PLL_MUTE;
on tile[AUDIO_IO_TILE]: port p_led_array = PORT_LED_ARRAY;

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS4384_I2C_ADDR, reg, data, 1, r_i2c_aud);}
#define ADC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS5368_I2C_ADDR, reg, data, 1, r_i2c_aud);}

#define CS2100_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c_aud);}
#define CS2100_REGREAD_ASSERT(reg, data, expected)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c_aud); assert(data[0] == expected);}
#define CS2100_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c_aud);}

#if defined (ADAT_RX) || defined(SPDIF_RX)
#define USE_FRACTIONAL_N 1

/* The number of timer ticks to wait for the audio PLL to lock */
/* CS2100 lists typical lock time as 100 * input period */
#define     AUDIO_PLL_LOCK_DELAY     (40000000)
#endif

#ifdef USE_FRACTIONAL_N
/* Init of CS2100 */
void PllInit(void)
{
    unsigned char data[1] = {0};

    /* Enable init */
    CS2100_REGWRITE(CS2100_DEVICE_CONFIG_1, 0x05); /* Note, board master clock on AUX_OUT */
    CS2100_REGWRITE(CS2100_GLOBAL_CONFIG, 0x01);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_1, 0x08);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_2, 0x00); //0x10 for always gen clock even when unlocked

    /* Read back and check */
    CS2100_REGREAD_ASSERT(CS2100_DEVICE_CONFIG_1, data, 0x05);
    CS2100_REGREAD_ASSERT(CS2100_GLOBAL_CONFIG, data, 0x01);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_1, data, 0x08);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_2, data, 0x00);
}

/* Setup PLL multiplier */
void PllMult(unsigned mult)
{
    unsigned char data[1] = {0};

    /* Multiplier is translated to 20.12 format by shifting left by 12 */
    CS2100_REGWRITE(CS2100_RATIO_1, (mult >> 12) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_2, (mult >> 4) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_3, (mult << 4) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_4, 0x00);

	/* Read back and check */
    CS2100_REGREAD_ASSERT(CS2100_RATIO_1, data, ((mult >> 12) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_2, data, ((mult >> 4) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_3, data, ((mult << 4) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_4, data, 0x00);
}
#endif

void AudioHwInit(chanend ?c_codec)
{
    /* Init the i2c module */
    i2c_master_init(r_i2c_aud);

    /* Assert reset to ADC and DAC */
    set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 0);
    set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 0);

    /* Turn on digital and analog supplies to DAC/ADC */
    set_gpio(p_pwr_pll_mute, P_VA_EN, 1);

    /* Wait for supply rail to settle */
    wait_us(5000); //5ms

#ifdef USE_FRACTIONAL_N
    /* Set clock source to CS Fractional-N clock multiplier */
    set_gpio(p_pwr_pll_mute, P_PLL_SEL, 1);
    /* If Initialise external PLL */
    PllInit();
#else
    /* Set clock source to on board clock rather than CS PLL */
    set_gpio(p_pwr_pll_mute, P_PLL_SEL, 0);
#endif

}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
	unsigned char data[1] = {0};

    /* Put ADC and DAC into reset */
	set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 0);
	set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 0);

#ifdef USE_FRACTIONAL_N
    /* Configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
    PllMult(mClk/300);

    /* Allow some time for mclk to lock and MCLK to stabilise - this is important to avoid glitches at start of stream */
    {
        timer t;
        unsigned time;
        t :> time;
        t when timerafter(time+AUDIO_PLL_LOCK_DELAY) :> void;
    }

    while(1)
    {
        /* Read Unlock Indicator in PLL as sanity check... */
        CS2100_REGREAD(CS2100_DEVICE_CONTROL, data);
        if(!(data[0] & 0x80))
        {
            break;
        }
    }
#else
    /* Set master clock select appropriately */
    if (mClk == MCLK_441)
    {
        set_gpio(p_adrst_cksel_dsd, P_F_SELECT, 0);
    }
    else
    {
        set_gpio(p_adrst_cksel_dsd, P_F_SELECT, 1); //mClk = MCLK_48
    }

    /* Allow MCLK to settle */
    wait_us(2000);
#endif


    if((dsdMode == DSD_MODE_NATIVE) || (dsdMode == DSD_MODE_DOP))
    {
        /* Enable DSD 8ch out mode on mux */
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 1);

        /* DAC out out reset, note ADC left in reset in for DSD mode */
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);

        /* Configure DAC values required for DSD mode */

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 1 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 1 for DSD
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0xe1);

        if (samFreq > 3000000)
        {
            /* DSD128 */
            /* DSD Control (Address: 0x04) */
            /* bit[7:5] : DSD Digital Inteface Format (DSD_DIF) : 128x over samples with 4x MCLK
             * bit[4] : Direct DSD Conversion: Set to 0, data sent to DSD processor
             * bit[3] : Static DSD detect : 1 for enabled
             * bit[2] : Invalid DSD Detect : 1 for enabled
             * bit[1] : DSD Phase Modulation Mode Select
             * bit[0] : DSD Phase Modulation Enable
             */
            DAC_REGWRITE(CS4384_DSD_CTRL, 0b11001100);
            set_led_array(LED_SQUARE_BIG);
        }
        else
        {
            /* DSD64 */
            /* DSD Control (Address: 0x04) */
            /* bit[7:5] : DSD Digital Inteface Format (DSD_DIF) : 64x over samples with 8x MCLK
             * bit[4] : Direct DSD Conversion: Set to 0, data sent to DSD processor
             * bit[3] : Static DSD detect : 1 for enabled
             * bit[2] : Invalid DSD Detect : 1 for enabled
             * bit[1] : DSD Phase Modulation Mode Select
             * bit[0] : DSD Phase Modulation Enable
             */
            DAC_REGWRITE(CS4384_DSD_CTRL, 0b01001100);
            set_led_array(LED_SQUARE_SML);
        }

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 0 for not freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 1 for DSD
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Power down disabled
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0xA0);

        /* Note: ADC kept in reset, no config sent. DSD mode is output only 0*/
    }
    else
    {
        /* dsdMode == 0 */
        /* Set MUX to PCM mode (muxes ADC I2S data lines) */
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 0);

        /* Configure DAC with PCM values. Note 2 writes to mode control to enable/disable freeze/power down */
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);//De-assert DAC reset

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 1 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 0 for PCM
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0b11000001);

#ifdef I2S_MODE_TDM
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b1100 for TDM
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x11 for auto-speed detect (32 to 200kHz)
        */
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b11000111);
#else
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b0001 for I2S up to 24bit
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x11 for auto-speed detect (32 to 200kHz)
        */
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b00010111);
#endif

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 0 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 0 for PCM
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Not powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0b10000000);

        /* Take ADC out of reset */
        set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 1);

        {
            unsigned dif = 0, mode = 0;
#ifdef I2S_MODE_TDM
            dif = 0x02;   /* TDM */
#else
            dif = 0x01;   /* I2S */
#endif

#ifdef CODEC_MASTER
            /* Note, only the ADC device supports being I2S master.
             * Set ADC as master and run DAC as slave */
            if(samFreq < 54000)
                mode = 0x00;     /* Single-speed Mode Master */
            else if(samFreq < 108000)
                mode = 0x01;     /* Double-speed Mode Master */
            else if(samFreq < 216000)
                mode = 0x02;     /* Quad-speed Mode Master */
#else
            mode = 0x03;    /* Slave mode all speeds */
#endif

            /* Reg 0x01: (GCTL) Global Mode Control Register */
            /* Bit[7]: CP-EN: Manages control-port mode
            * Bit[6]: CLKMODE: Setting puts part in 384x mode
            * Bit[5:4]: MDIV[1:0]: Set to 01 for /2
            * Bit[3:2]: DIF[1:0]: Data Format: 0x01 for I2S, 0x02 for TDM
            * Bit[1:0]: MODE[1:0]: Mode: 0x11 for slave mode
            */
            ADC_REGWRITE(CS5368_GCTL_MDE, 0b10010000 | (dif << 2) | mode);
        }

        /* Reg 0x06: (PDN) Power Down Register */
        /* Bit[7:6]: Reserved
         * Bit[5]: PDN-BG: When set, this bit powers-own the bandgap reference
         * Bit[4]: PDM-OSC: Controls power to internal oscillator core
         * Bit[3:0]: PDN: When any bit is set all clocks going to that channel pair are turned off
         */
        ADC_REGWRITE(CS5368_PWR_DN, 0b00000000);

        /* Illuminate LEDs based on sample-rate */
        if (samFreq > 192000)
        {
            set_led_array(LED_ALL_ON);
        }
        else if (samFreq > 96000)
        {
            set_led_array(LED_ROW_3);
        }
        else if (samFreq > 48000)
        {
            set_led_array(LED_ROW_2);
        }
        else
        {
            set_led_array(LED_ROW_1);
        }
    }

    /* De-assert MUTE lines (Only connected to testpoints on audio8 slice) */
    set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 0);

    return;
}
//:
