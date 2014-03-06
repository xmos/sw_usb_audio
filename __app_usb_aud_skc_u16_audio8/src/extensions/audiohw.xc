#include <xs1.h>
#include "devicedefines.h"
#include <platform.h>
#include "gpio.h"
#include "cs4384.h"
#include "cs5368.h"
#include "print.h"

/* I2C bus to DAC */
on tile[AUDIO_IO_TILE]: struct r_i2c r_i2c_aud = { PORT_I2C_SCL_AUD, PORT_I2C_SDA_AUD };


on tile[AUDIO_IO_TILE]: port p_adrst_cksel_dsd = PORT_CODEC_RST_CLKSEL_DSD;
on tile[AUDIO_IO_TILE]: port p_pwr_pll_mute = PORT_PWR_PLL_MUTE;
on tile[AUDIO_IO_TILE]: port p_led_array = PORT_LED_ARRAY;

//Arrays of reg addresses and associated data arrays, which are initialsed for startup/initial config
static unsigned char reg_addr_cs4384[] = {CS4384_MODE_CTRL, CS4384_PCM_CTRL, CS4384_DSD_CTRL, CS4384_MODE_CTRL};
static unsigned char reg_data_cs4384[] = {CS4384_MODE_CTRL_PCM, CS4384_PCM_CTRL_PCM, CS4384_DSD_CTL_DSD1x,
                                            CS4384_MODE_CTL2_PCM};

static unsigned char reg_addr_cs5368[] = {CS5368_GCTL_MDE, CS5368_OVFL_ST, CS5368_OVFL_MSK, CS5368_HPF_CTRL,
                                            CS5368_PWR_DN, CS5368_MUTE_CTRL, CS5368_SDO_EN};
static unsigned char reg_data_cs5368[] = {CS5368_GCTL_MDE_VAL, CS5368_OVFL_ST_VAL, CS5368_OVFL_MSK_VAL,
                                            CS5368_HPF_CTRL_VAL, CS5368_PWR_DN_VAL, CS5368_MUTE_CTRL_VAL, CS5368_SDO_EN_VAL};

#define VERIFY_I2C 1

/* Write array of register to i2c device */
int i2c_slave_configure(int codec_addr, int num_writes, unsigned char reg_addr[], unsigned char reg_data[], struct r_i2c &r_i2c)
{
    int success = 1;
    unsigned char data[1];

    for(int i = 0; i < num_writes; i++){
        data[0] = reg_data[i];
        success &= i2c_master_write_reg(codec_addr, reg_addr[i], data, 1, r_i2c);
#if VERIFY_I2C==1
        if (success == 0) {
            printstr("ACK failed on I2C write to device 0x");
            printhex(codec_addr);
            printstr(", reg address 0x");
            printhexln(reg_addr[i]);
        }
        i2c_master_read_reg(codec_addr, reg_addr[i], data, 1, r_i2c);
        if (data[0] != reg_data[i]){
            printstr("ERROR");
            printstr(" verifying I2C device 0x");
            printhex(codec_addr);
            printstr(" register address 0x");
            printhex(reg_addr[i]);
            printstr(". Expected 0x");
            printhex(reg_data[i]);
            printstr(", received 0x");
            printhexln(data[0]);
        }
#endif
    }
    return(success);
}


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
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode)
{
	unsigned char data[1] = {0};

    /* PutA DC and DAC into reset */
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
    wait_us(2000); // 2ms

    if (dsdMode)
    {
        /* Enable DSD 8ch out mode on mux */
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 1);

        /* DAC out out reset, note ADC in reset in DSD mode */
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);


        /* Configure DAC with DSD values. Note 2 writes to mode control to enable/disable freeze/power down */
        reg_data_cs4384[0] = CS4384_MODE_CTRL_DSD;
        if (samFreq > 3000000)
        {
            /* DSD128 */
            reg_data_cs4384[2] = CS4384_DSD_CTL_DSD2x;
            p_led_array <: LED_SQUARE_BIG;
        }
        else
        {
            /* DSD64 */
            reg_data_cs4384[2] = CS4384_DSD_CTL_DSD1x;
            p_led_array <: LED_SQUARE_SML;
        }
        reg_data_cs4384[3] = CS4384_MODE_CTL2_DSD;

        /* Write registers via i2c */
        i2c_slave_configure(CS4384_I2C_ADDR, sizeof(reg_addr_cs4384), reg_addr_cs4384, reg_data_cs4384, r_i2c_aud);

        //Note ADC kept in reset, no config sent. DSD mode is output only
    }
    else
    {
        /* dsdMode == 0 */
        /* Set MUX to DSD mode (muxes ADC I2S data lines) */
        set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 0);

        /* Configure DAC with PCM values. Note 2 writes to mode control to enable/disable freeze/power down */
        set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);//De-assert DAC reset
        reg_data_cs4384[0] = CS4384_MODE_CTRL_PCM;
        reg_data_cs4384[1] = CS4384_PCM_CTRL_PCM;
        reg_data_cs4384[3] = CS4384_MODE_CTL2_PCM;
        i2c_slave_configure(CS4384_I2C_ADDR, sizeof(reg_addr_cs4384), reg_addr_cs4384, reg_data_cs4384, r_i2c_aud);

        /* Configure ADC with default values. */
        set_gpio(p_adrst_cksel_dsd, P_ADC_RST_N, 1);//De-assert ADC reset
        reg_data_cs5368[0] = CS5368_GCTL_MDE_VAL;
        i2c_slave_configure(CS5368_I2C_ADDR, sizeof(reg_addr_cs5368), reg_addr_cs5368, reg_data_cs5368, r_i2c_aud);

        p_led_array <: LED_ROW_1;
        if (samFreq > 48000) p_led_array <: LED_ROW_2;
        if (samFreq > 96000) p_led_array <: LED_ROW_3;
        if (samFreq > 192000) p_led_array <: LED_ALL_ON;
    }

    /* De-assert MUTE lines (Only connected to testpoints on audio8 slice) */
    set_gpio(p_pwr_pll_mute, P_MUTE_A | P_MUTE_B, 0);

#ifdef CODEC_MASTER
#error not currently implemented
#endif
    return;
}
//:
