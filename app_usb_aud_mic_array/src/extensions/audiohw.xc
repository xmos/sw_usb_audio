#include <xs1.h>

#include <assert.h>
#include "devicedefines.h"
#include <platform.h>
#include "i2c_shared.h"
#include "cs2100.h"
#include "print.h"

on tile[AUDIO_IO_TILE] : out port p_pll_clk = PORT_PLL_REF;

/* 0: DAC reset */
/* 1: Ethernet Phy reset */
on tile[1] : out port p_gpio = XS1_PORT_4F;

on tile [1] : struct r_i2c r_i2c = {XS1_PORT_4E};
 
#define CS2100_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}
#define CS2100_REGREAD_ASSERT(reg, data, expected)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c); assert(data[0] == expected);}
#define CS2100_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(0x4a, reg, data, 1, r_i2c);}
#define DAC_REGREAD_ASSERT(reg, data, expected)  {data[0] = 0xAA; i2c_master_read_reg(0x4a, reg, data, 1, r_i2c); assert(data[0] == expected);}


/* The number of timer ticks to wait for the audio PLL to lock */
/* CS2100 lists typical lock time as 100 * input period */
#define AUDIO_PLL_LOCK_DELAY     (40000000)

/* Frequency (in Hz) of the sync clock the xCORE drives to the external PLL */
#define PLL_SYNC_FREQ            (1000000)

/* Init of CS2100 */
void PllInit(void)
{
    unsigned char data[1] = {0};

    /* Enable init */
    CS2100_REGWRITE(CS2100_DEVICE_CONFIG_1, 0x05);
    CS2100_REGWRITE(CS2100_GLOBAL_CONFIG, 0x01);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_1, 0x08);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_2, 0x00); //0x10 for always gen clock even when unlocked

    /* Read back and check */
    CS2100_REGREAD_ASSERT(CS2100_DEVICE_CONFIG_1, data, 0x05);
    CS2100_REGREAD_ASSERT(CS2100_GLOBAL_CONFIG, data, 0x01);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_1, data, 0x08);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_2, data, 0x00);
}

/* Setup ratio in external PLL */
void PllMult(unsigned output, unsigned ref)
{
    unsigned char data[1] = {0};

    /* PLL expects 12:20 format, convert output and ref to 12:20 */
    /* Shift up the dividend by 12 to retain format... */
    unsigned mult = (unsigned) ((((unsigned long long)output) << 32) / (((unsigned long long)ref) << 20));

    CS2100_REGWRITE(CS2100_RATIO_1, (mult >> 24) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_2, (mult >> 16) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_3, (mult >> 8) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_4, (mult & 0xFF));

	/* Read back and check */
    CS2100_REGREAD_ASSERT(CS2100_RATIO_1, data, ((mult >> 24) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_2, data, ((mult >> 16) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_3, data, ((mult >> 8) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_4, data, (mult & 0xFF));
}

/* Core to generate 300Hz reference to CS2100 PLL */
void genclock()
{
    timer t;
    unsigned time;
    unsigned pinVal = 0;

    t :> time;
    while(1)
    {
        p_pll_clk <: pinVal;
        pinVal = ~pinVal;
        time += (XS1_TIMER_HZ/PLL_SYNC_FREQ/2); // E.g. 166667 for 300Hz;
        t when timerafter(time) :> void;
    }
}

void wait_us(int microseconds)
{
    timer t;
    unsigned time;

    t :> time;
    t when timerafter(time + (microseconds * 100)) :> void;
}

void AudioHwInit(chanend ?c_codec)
{
    /* DAC in reset */
    p_gpio <: 0;
    
    /* Init the i2c module */
    i2c_shared_master_init(r_i2c);

    /* Initialise external PLL */
    PllInit();
    
    /* Configure external fractional-n clock multiplier for PLL_SYNC_FREQ Hz -> mClkFreq */
    PllMult(DEFAULT_MCLK_FREQ, PLL_SYNC_FREQ);

    /* Allow some time for mclk to lock and MCLK to stabilise - this is important to avoid glitches at start of stream */
    {
        timer t;
        unsigned time;
        t :> time;
        t when timerafter(time+AUDIO_PLL_LOCK_DELAY) :> void;
    }

}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
	unsigned char data[1] = {0};

    /* DAC in reset */
    p_gpio <: 0;

    /* Configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
    PllMult(mClk, PLL_SYNC_FREQ);

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

    /* DAC out of reset */
    p_gpio <: 1;
    {
        timer t;
        unsigned time;
        t :> time;
        t when timerafter(time+100000) :> void;
    } 

    /* Write to PDN bit 1 in under 10ms or DAC will enter HW mode */
    unsigned char val = 0b00000001;
    DAC_REGWRITE(2, val);
    DAC_REGREAD_ASSERT(2, data, val);

    /* Put DAC into slave mode  */
    val = 0b00001000;
    DAC_REGWRITE(4, val);
    DAC_REGREAD_ASSERT(4, data, val);

    /* Set PDN bit low */
    val = 0b00000000;
    DAC_REGWRITE(2, val);
    DAC_REGREAD_ASSERT(2, data, val);
    
    return;
}
//:
