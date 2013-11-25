#include <xs1.h>
#include <print.h>
#include <platform.h>
#include <assert.h>
#include "devicedefines.h"
#include "i2c.h"

/* I2C ports */
on tile[AUDIO_IO_TILE]: struct r_i2c i2cPorts = {PORT_I2C_SCL, PORT_I2C_SDA}; 

/* Reference clock to external fractional-N clock multiplier */
on tile[AUDIO_IO_TILE]: out port p_pll_ref    = PORT_PLL_REF;

on tile[AUDIO_IO_TILE]: out port p_aud_cfg    = PORT_AUD_CFG;

//#define PLL_DEV_ADR        (0x9C>>1)   
//#define COD_DEV_ADRS       (0x90>>1)

#define PLL_DEV_ADR        0x9C
#define COD_DEV_ADRS       0x90


unsigned char pllRead(unsigned char reg)
{
    unsigned char data[1] = {0};
    i2c_master_read_reg(PLL_DEV_ADR, reg, data, 1, i2cPorts); 
    return data[0];
}

#define PLL_REGRD(reg) 		pllRead(reg)
#define PLL_REGWR(reg, val) {data[0] = val; i2c_master_write_reg(PLL_DEV_ADR, reg, data, 1, i2cPorts);}

/* Init of CS2300 */
void PllInit(void)
{
    unsigned char data[1] = {0};

    /* Enable init */
    //PLL_REGWR(0x1e, 0b01110000); // increase pll bandwidth to reduce lock time
    PLL_REGWR(0x03, 0x07);
    PLL_REGWR(0x05, 0x01);
    PLL_REGWR(0x16, 0x10);
    //    PLL_REGWR(0x17, 0x10); //0x10 for always gen clock even when unlocked
    PLL_REGWR(0x17, 0x00); //0x10 for always gen clock even when unlocked


    /* Check */
    assert(PLL_REGRD(0x03) == 0x07);
    assert(PLL_REGRD(0x05) == 0x01);
    assert(PLL_REGRD(0x16) == 0x10);
    assert(PLL_REGRD(0x17) == 0x00);
    //assert(PLL_REGRD(0x1e) == 0b01110000);
}

/* Setup PLL multiplier */
void PllMult(unsigned mult)
{
    unsigned char data[1] = {0};
	
    /* Multiplier is translated to 20.12 format by shifting left by 12 */
    PLL_REGWR(0x06, (mult >> 12) & 0xFF);
    PLL_REGWR(0x07, (mult >> 4) & 0xFF);
    PLL_REGWR(0x08, (mult << 4) & 0xFF);
    PLL_REGWR(0x09, 0x00);

	/* Check */
    assert(PLL_REGRD(0x06) == ((mult >> 12) & 0xFF));
    assert(PLL_REGRD(0x07) == ((mult >> 4) & 0xFF));
    assert(PLL_REGRD(0x08) == ((mult << 4) & 0xFF));
    assert(PLL_REGRD(0x09) == 0x00);
}


/* CODEC initialisation for Cirrus Logic CS42448 */
void AudioHwInit(chanend ?c_codec) 
{
    unsigned char tmp[1];

    /* Clock buffers and CODEC out of reset */
#ifndef CODEC_MASTER
    p_aud_cfg <: 0b1000;
#else
    p_aud_cfg <: 0b1010;
#endif

    PllInit();

    /* Power Control Register (Address 02h) */
    /* 0    Power Down                           (PDN)   = 1 Enable, 0 Disable */  
    /* 1:4  Power Down DAC Pairs            (PDN_DACX)   = 1 Enable, 0 Disable */
    /* 5:7  Power Down ADC Pairs            (PDN_ADCX)   = 1 Enable, 0 Disable */
    tmp[0] = 0x01;
    i2c_master_write_reg(COD_DEV_ADRS, 0x2, tmp, 1, i2cPorts);

    /* Interface Formats Register (Address 04h)             */
    /* 0    Freeze Controls                    (FREEZE)     = 0,               */
    /* 1    Auxiliary Digital Interface Format (AUX_DIF)    = 0, */
    /* 2:4  DAC Digital Interface Format       (DAC_DIF)    = 010 (Right justified, 24bit) */
    /* 5:7  ADC Digital Interface Format       (ADC_DIF)    = 010 (Rigth justified, 24bit) */
    tmp[0] = 0x49;
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

    /* Power Control Register (Address 02h) - PDN disable */
    tmp[0] = 0x00;
    i2c_master_write_reg(COD_DEV_ADRS, 0x2, tmp, 1, i2cPorts);

    return;
}

void genclock()
{
    timer t;
    unsigned time;
    unsigned pinVal = 0;

    #warning RM ME!!
    t :> time;
    while(1)
    {
        p_pll_ref <: pinVal;
        pinVal = ~pinVal;
        time += 166667;
        t when timerafter(time) :> void; 
    }

}


/* 
 * Configures the Audio Hardware  for the required sample frequency.  
 *
 * CODEC configuration for sample frequency change for Cirrus Logic CS42448 
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode)
{
    unsigned char tmp[1];
 
    /* For L2 reference design configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
    PllMult(mClk/300);
    
    /* Functional Mode (Address 03h) */
    /* 0:1  DAC Functional Mode                    Slave:Auto-detect samp rate      11 */
    /* 2:3  ADC Functional Mode                    Slave:Auto -detect samp rate     11 */
    /*                                             Master: Single                   00 */
    /*                                             Master: Double                   01 */
    /*                                             Master: Quad                     10 */
    /* 4:6  MCLK Frequency                         256/128/64 :                    000 */
    /*                                             512/256/128:                    010 */
    /* 7                                           Reserved                            */
#ifndef CODEC_MASTER
    tmp[0] = 0b11110000;                                             /* Autodetect */
#else
    if(samFreq < 50000)
    {
        tmp[0] = 0b00000000;
    }
    else if(samFreq < 100000)
    {
        tmp[0] = 0b01010000;
    }
    else
    {
        tmp[0] = 0b10100000;
    }
#endif
    if(mClk < 15000000)
    {
        tmp[0] |= 0;                   // 256/128/64
    }
    else if(mClk < 25000000)
    {
        tmp[0] |= 0b00000100;            // 512/256/128
    }
    else
    {
        printstrln("Err: MCLK currently not supported");
    }

    i2c_master_write_reg(COD_DEV_ADRS, 0x3, tmp, 1, i2cPorts);
}
