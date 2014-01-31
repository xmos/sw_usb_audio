#include <xs1.h>
#include "devicedefines.h"
#include <platform.h>
#include "gpio.h"
#include "cs4384.h"
#include "cs5368.h"
#include "print.h"

on tile[AUDIO_IO_TILE]: struct r_i2c p_i2c = { PORT_I2C_SCL, PORT_I2C_SDA };
on tile[AUDIO_IO_TILE]: port p_adrst_cksel_dsd = PORT_CODEC_RST_CLKSEL_DSD;
on tile[AUDIO_IO_TILE]: port p_pwr_pll_mute = PORT_PWR_PLL_MUTE;
on tile[AUDIO_IO_TILE]: port p_led_array = PORT_LED_ARRAY;

//Arrays of reg addresses and associated data arrays, which are initialsed for startup/initial config
static unsigned char reg_addr_cs4384[] = {CS4384_MODE_CTRL, CS4384_PCM_CTRL, CS4384_DSD_CTRL, CS4384_MODE_CTRL};
static unsigned char reg_data_cs4384[] = {CS4384_MODE_CTRL_PCM, CS4384_PCM_CTRL_PCM, CS4384_DSD_CTL_DSD1x, CS4384_MODE_CTL2_PCM};

static unsigned char reg_addr_cs5368[] = {CS5368_GCTL_MDE, CS5368_OVFL_ST, CS5368_OVFL_MSK, CS5368_HPF_CTRL, CS5368_PWR_DN, CS5368_MUTE_CTRL, CS5368_SDO_EN};
static unsigned char reg_data_cs5368[] = {CS5368_GCTL_MDE_VAL, CS5368_OVFL_ST_VAL, CS5368_OVFL_MSK_VAL, CS5368_HPF_CTRL_VAL, CS5368_PWR_DN_VAL, CS5368_MUTE_CTRL_VAL, CS5368_SDO_EN_VAL};

void AudioHwInit(chanend ?c_codec) 
{
  
    //Set MUTE lines high - only connected to test points on XA-SK-AUDIO8
    //set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 1);

    //assert reset to ADC and DAC
    set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 0);
    set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 0);

    //Turn on digital and analog supplies to DAC/ADC
    set_gpio(p_pwr_pll_mute, P_VA_EN, 1);

    //Ensure clock source is on board clock rather than CS PLL
    set_gpio(p_pwr_pll_mute, P_PLL_SEL, 0);

    //Wait for supply rail to settle
    wait_us(5000); //5ms

    //Init PLL
    //audio_clock_CS2100CP_init(p_i2c, MASTER_TO_WORDCLOCK_RATIO);

    //Init DAC - sends string of init commands
    //set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);//De-assert reset
    //i2c_slave_configure(CS4384_I2C_ADDR, sizeof(reg_addr_cs4384), reg_addr_cs4384, reg_data_cs4384, p_i2c);

    //Init ADC - sends string of init commands
    //set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 1);//De-assert reset
    //i2c_slave_configure(CS5368_I2C_ADDR, sizeof(reg_addr_cs5368), reg_addr_cs5368, reg_data_cs5368, p_i2c);
    
	//Set MUTE lines low - only connected to test points on XA-SK-AUDIO8
    //set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 0);
}

/* Configures the external audio hardware for the required sample frequency.  
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode)
{
	unsigned char data[1] = {0};

    //Assert MUTE lines (although not actually connected to anything)
    set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 1);

    //assert reset to ADC and DAC
	set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 0);
	set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 0);

    //Ed test - see if built in mute control does it in DAC
    //unsigned char data[1] = {CS4384_ALLMUTE_PCM};
    //i2c_master_write_reg(CS4384_I2C_ADDR, CS4384_MUTE_CTRL, data, 1, p_i2c);
    //wait_us(1000); //1ms wait for MUTE to kick in

    // Set master clock select appropriately 
    if (mClk == MCLK_441)  set_gpio(p_adrst_cksel_dsd, P_F_SELECT, 0);
    else set_gpio(p_adrst_cksel_dsd, P_F_SELECT, 1); //mClk = MCLK_48

    wait_us(1000); //1ms wait for MCLK to settle     

    if (dsdMode){
        //Enable DSD 8ch out mode on mux
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 1);

        //Configure DAC with DSD values. Note 2 writes to mode control to enable/disable freeze/power down 
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);//De-assert DAC reset
        reg_data_cs4384[0] = CS4384_MODE_CTRL_DSD;
        //Note cs4384[1] is don't care 
        if (samFreq > 3000000){  //DSD128
            reg_data_cs4384[2] = CS4384_DSD_CTL_DSD2x;
            p_led_array <: LED_SQUARE_BIG;
        }
        else {                   //DSD64
            reg_data_cs4384[2] = CS4384_DSD_CTL_DSD1x;
            p_led_array <: LED_SQUARE_SML;
        }
        reg_data_cs4384[3] = CS4384_MODE_CTL2_DSD;
        i2c_slave_configure(CS4384_I2C_ADDR, sizeof(reg_addr_cs4384), reg_addr_cs4384, reg_data_cs4384, p_i2c);

        //Note ADC kept in reset, no config sent. DSD mode is output only
    }

    else { //dsdMode == 0  
        //Disable DSD-normal 8i8o over I2S instead / PCM
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 0);

        //Configure DAC with PCM values. Note 2 writes to mode control to enable/disable freeze/power down 
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);//De-assert DAC reset        
        reg_data_cs4384[0] = CS4384_MODE_CTRL_PCM;
        reg_data_cs4384[1] = CS4384_PCM_CTRL_PCM;
        //Note cs_4384[2] is don't care
        reg_data_cs4384[3] = CS4384_MODE_CTL2_PCM;
        i2c_slave_configure(CS4384_I2C_ADDR, sizeof(reg_addr_cs4384), reg_addr_cs4384, reg_data_cs4384, p_i2c);

        //Configure ADC with default values.
        set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 1);//De-assert ADC reset
        reg_data_cs5368[0] = CS5368_GCTL_MDE_VAL;
        i2c_slave_configure(CS5368_I2C_ADDR, sizeof(reg_addr_cs5368), reg_addr_cs5368, reg_data_cs5368, p_i2c);

        p_led_array <: LED_ROW_1;
        if (samFreq > 48000) p_led_array <: LED_ROW_2;
        if (samFreq > 96000) p_led_array <: LED_ROW_3;
        if (samFreq > 192000) p_led_array <: LED_ALL_ON;
    }

    //De-assert MUTE lines (although not actually connected to anything on audio8 slice)
    set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 0);

    //Ed test - trying out internal mute in DAC
   // data[0] = CS4384_UNMUTE_PCM;
    //i2c_master_write_reg(CS4384_I2C_ADDR, CS4384_MUTE_CTRL, data, 1, p_i2c);

#ifdef CODEC_MASTER
#error not currently implemented
#endif 
    return;
}
//:
