#include <xs1.h>
#include <print.h>
#include <platform.h>
#include <assert.h>
#include "devicedefines.h"
#include "i2c.h"

/* I2C ports */
on tile[AUDIO_IO_TILE]: struct r_i2c i2cPorts = {PORT_I2C_SCL, PORT_I2C_SDA};

#if !(defined(SPDIF_RX) || defined (ADAT_RX))
/* Reference clock to external fractional-N clock multiplier */
on tile[AUDIO_IO_TILE]: out port p_pll_ref    = PORT_PLL_REF;
#endif


on tile[AUDIO_IO_TILE]: out port p_aud_cfg    = PORT_AUD_CFG;

#define CS2300_I2C_DEVICE_ADDR      (0x9c>>1)
#define COD_DEV_ADRS                (0x90>>1)

#define CS2300_DEVICE_CONTROL       0x02
#define CS2300_DEVICE_CONFIG_1      0x03
#define CS2300_GLOBAL_CONFIG        0x05
#define CS2300_RATIO_1              0x06
#define CS2300_RATIO_2              0x07
#define CS2300_RATIO_3              0x08
#define CS2300_RATIO_4              0x09
#define CS2300_FUNC_CONFIG_1        0x16
#define CS2300_FUNC_CONFIG_2        0x17

#define CS2300_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(CS2300_I2C_DEVICE_ADDR, reg, data, 1, i2cPorts);}
#define CS2300_REGREAD_ASSERT(reg, data, expected)  {data[0] = 0xAA; i2c_master_read_reg(CS2300_I2C_DEVICE_ADDR, reg, data, 1, i2cPorts); assert(data[0] == expected);}
#define CS2300_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS2300_I2C_DEVICE_ADDR, reg, data, 1, i2cPorts);}

/* The number of timer ticks to wait for the audio PLL to lock */
/* CS2300 lists typical lock time as 100 * input period */
#define AUDIO_PLL_LOCK_DELAY     (40000000)

/* Init of CS2300 */
void PllInit(void)
{
    unsigned char data[1] = {0};

    /* Enable init */
    CS2300_REGWRITE(CS2300_DEVICE_CONFIG_1, 0x07);
    CS2300_REGWRITE(CS2300_GLOBAL_CONFIG, 0x01);
    CS2300_REGWRITE(CS2300_FUNC_CONFIG_1, 0x10);
    CS2300_REGWRITE(CS2300_FUNC_CONFIG_2, 0x00); //0x10 for always gen clock even when unlocked

    /* Read back and check */
    CS2300_REGREAD_ASSERT(CS2300_DEVICE_CONFIG_1, data, 0x07);
    CS2300_REGREAD_ASSERT(CS2300_GLOBAL_CONFIG, data, 0x01);
    CS2300_REGREAD_ASSERT(CS2300_FUNC_CONFIG_1, data, 0x10);
    CS2300_REGREAD_ASSERT(CS2300_FUNC_CONFIG_2, data, 0x00);
}

/* Setup PLL multiplier */
void PllMult(unsigned mult)
{
    unsigned char data[1] = {0};

    /* Multiplier is translated to 20.12 format by shifting left by 12 */
    CS2300_REGWRITE(CS2300_RATIO_1, (mult >> 12) & 0xFF);
    CS2300_REGWRITE(CS2300_RATIO_2, (mult >> 4) & 0xFF);
    CS2300_REGWRITE(CS2300_RATIO_3, (mult << 4) & 0xFF);
    CS2300_REGWRITE(CS2300_RATIO_4, 0x00);

	/* Read back and check */
    CS2300_REGREAD_ASSERT(CS2300_RATIO_1, data, ((mult >> 12) & 0xFF));
    CS2300_REGREAD_ASSERT(CS2300_RATIO_2, data, ((mult >> 4) & 0xFF));
    CS2300_REGREAD_ASSERT(CS2300_RATIO_3, data, ((mult << 4) & 0xFF));
    CS2300_REGREAD_ASSERT(CS2300_RATIO_4, data, 0x00);
}


/* CODEC initialisation for Cirrus Logic CS42448 */
void AudioHwInit(chanend ?c_codec)
{
    i2c_master_init(i2cPorts);

    /* Initialise external PLL */
    PllInit();

    return;
}

#if !(defined(SPDIF_RX) || defined(ADAT_RX))
/* Core to generate 300Hz reference to CS2300 PLL */
void genclock()
{
    timer t;
    unsigned time;
    unsigned pinVal = 0;

    t :> time;
    while(1)
    {
        p_pll_ref <: pinVal;
        pinVal = ~pinVal;
        time += 166667;
        t when timerafter(time) :> void;
    }
}
#endif

/*
 * Configures the Audio Hardware  for the required sample frequency.
 *
 * CODEC configuration for sample frequency change for Cirrus Logic CS42448
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned samRes_DAC, unsigned samRes_ADC)
{
    unsigned char tmp[1] = {0};

    /* Clock buffers and CODEC into reset */
#ifndef CODEC_MASTER
    p_aud_cfg <: 0b0000;
#else
    p_aud_cfg <: 0b0010;
#endif

    /* For L2 reference design configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
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
        CS2300_REGREAD(CS2300_DEVICE_CONTROL, tmp);
        if(!(tmp[0] & 0x80))
        {
            break;
        }
    }

    /* Clock buffers and CODEC out of reset */
#ifndef CODEC_MASTER
    p_aud_cfg <: 0b1000;
#else
    p_aud_cfg <: 0b1010;
#endif

    /* Power Control Register (Address 02h) */
    /* 0    Power Down                           (PDN)   = 1 Enable, 0 Disable */
    /* 1:4  Power Down DAC Pairs            (PDN_DACX)   = 1 Enable, 0 Disable */
    /* 5:7  Power Down ADC Pairs            (PDN_ADCX)   = 1 Enable, 0 Disable */
    tmp[0] = 0x01;
    i2c_master_write_reg(COD_DEV_ADRS, 0x2, tmp, 1, i2cPorts);

#ifdef I2S_MODE_TDM
#ifdef CODEC_MASTER
#error CODEC supports slave mode only in TDM mode
#endif
  /* Interface Formats Register (Address 04h)             */
    /* 0:2  ADC Digital Interface Format       (ADC_DIF)    = 110 (TDM, 24bit) */
    /* 3:5  DAC Digital Interface Format       (DAC_DIF)    = 110 (TDM, 24bit) */
    /* 6    Auxiliary Digital Interface Format (AUX_DIF)    = 1, (I2S)         */
    /* 7    Freeze Controls                    (FREEZE)     = 0,               */
    tmp[0] = 0x76;
#else
    /* Interface Formats Register (Address 04h)             */
    /* 0:2  ADC Digital Interface Format       (ADC_DIF)    = 001 (I2S, 24bit) */
    /* 3:5  DAC Digital Interface Format       (DAC_DIF)    = 001 (I2S, 24bit) */
    /* 6    Auxiliary Digital Interface Format (AUX_DIF)    = 1, (I2S)         */
    /* 7    Freeze Controls                    (FREEZE)     = 0,               */
    tmp[0] = 0x49;
#endif
    i2c_master_write_reg(COD_DEV_ADRS, 0x4, tmp, 1, i2cPorts);

    /* ADC Control & DAC De-Emphasis (Address 05h) */
    /* 0   ADC1-2_HPF FREEZE = 0, */
    /* 1   ADC3_HPF FREEZE = 0, */
    /* 2   DAC_DEM = 0, */
    /* 3   ADC1_SINGLE = 1(single ended), */
    /* 4   ADC2_SINGLE = 1, */
    /* 5   ADC3_SINGLE = 1, */
    /* 6   AIN5_MUX = 0, */
    /* 7   AIN6_MUX = 0 */
    tmp[0] = 0x1C;
    i2c_master_write_reg(COD_DEV_ADRS, 0x5, tmp, 1, i2cPorts);

    /* Functional Mode (Address 03h) */
    /* 0                                           Reserved                            */
    /* 3:1  MCLK Frequency                         256/128/64 :                    000 */
    /*                                             512/256/128:                    010 */
    /* 5:4  ADC Functional Mode                    Slave:  Auto-detect samp rate    11 */
    /*                                             Master: Single                   00 */
    /*                                             Master: Double                   01 */
    /*                                             Master: Quad                     10 */
    /* 7:6  DAC Functional Mode                    Slave:  Auto-detect samp rate    11 */
    /*                                             Master: Single                   00 */
    /*                                             Master: Double                   01 */
    /*                                             Master: Quad                     10 */
#ifndef CODEC_MASTER
    /* Autodetect */
    tmp[0] = 0b11110000;
#else
    if(samFreq < 50000)
    {
        /* Single */
        tmp[0] = 0b00000000;
    }
    else if(samFreq < 100000)
    {
        /* Double */
        tmp[0] = 0b01010000;
    }
    else
    {
        /* Quad */
        tmp[0] = 0b10100000;
    }
#endif
    if(mClk < 15000000)
    {
        tmp[0] |= 0;                      // 256/128/64
    }
    else if(mClk < 25000000)
    {
        tmp[0] |= 0b00000100;             // 512/256/128
    }
    else if(mClk < 51000000)
    {
        tmp[0] |= 0b00001000;             // 1024/512/256
    }
    else
    {
        printstrln("Err: AudioHWConfig(): Mclk freq not supported");
    }

    i2c_master_write_reg(COD_DEV_ADRS, 0x3, tmp, 1, i2cPorts);

    /* Power Control Register (Address 02h) - PDN disable */
    tmp[0] = 0x00;
    i2c_master_write_reg(COD_DEV_ADRS, 0x2, tmp, 1, i2cPorts);
}
