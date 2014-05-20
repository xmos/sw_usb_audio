#include <xs1.h>
#include "devicedefines.h"
#include <platform.h>
#include "gpio.h"
#include "cs4384.h"
#include "cs5368.h"
#include "print.h"
#include "dsd_support.h"

/* I2C bus to DAC */
on tile[AUDIO_IO_TILE]: struct r_i2c r_i2c_aud = { PORT_I2C_SCL_AUD, PORT_I2C_SDA_AUD };

on tile[AUDIO_IO_TILE]: port p_adrst_cksel_dsd = PORT_CODEC_RST_CLKSEL_DSD;
on tile[AUDIO_IO_TILE]: port p_pwr_pll_mute = PORT_PWR_PLL_MUTE;
on tile[AUDIO_IO_TILE]: port p_led_array = PORT_LED_ARRAY;

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS4384_I2C_ADDR, reg, data, 1, r_i2c_aud);}
#define ADC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS5368_I2C_ADDR, reg, data, 1, r_i2c_aud);}

void AudioHwInit(chanend ?c_codec)
{
    /* Init the i2c module */
    i2c_master_init(r_i2c_aud);

    /* Assert reset to ADC and DAC */
    set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 0);
    set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 0);

    /* Turn on digital and analog supplies to DAC/ADC */
    set_gpio(p_pwr_pll_mute, P_VA_EN, 1);

    /* Set clock source to on board clock rather than CS PLL */
    set_gpio(p_pwr_pll_mute, P_PLL_SEL, 0);

    /* Wait for supply rail to settle */
    wait_us(5000); //5ms
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
            p_led_array <: LED_SQUARE_BIG;
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
            p_led_array <: LED_SQUARE_SML;
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
        /* Set MUX to DSD mode (muxes ADC I2S data lines) */
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
        
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b0001 for I2S up to 24bit
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x11 for auto-speed detect (32 to 200kHz)
        */ 
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b00010111);
       
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

        /* Reg 0x01: (GCTL) Global Mode Control Register */
        /* Bit[7]: CP-EN: Manages control-port mode
         * Bit[6]: CLKMODE: Setting puts part in 384x mode
         * Bit[5:4]: MDIV[1:0]: Set to 01 for /2 
         * Bit[3:2]: DIF[1:0]: Data Format: 0x01 for I2S 
         * Bit[1:0]: MODE[1:0]: Mode: 0x11 for slave mode 
         */
        ADC_REGWRITE(CS5368_GCTL_MDE, 0b10010111);

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
            p_led_array <: LED_ALL_ON;
        }
        else if (samFreq > 96000) 
        {
            p_led_array <: LED_ROW_3;
        }
        else if (samFreq > 48000)
        {
            p_led_array <: LED_ROW_2;
        }
        else
        {
            p_led_array <: LED_ROW_1;
        }
    }

    /* De-assert MUTE lines (Only connected to testpoints on audio8 slice) */
    set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 0);

#ifdef CODEC_MASTER
#error not currently implemented
#endif
    return;
}
//:
