#include "devicedefines.h"
#include "iic.h"
#include <print.h>

#include "iicports.h"

extern out port p_aud_cfg;

#define COD_DEV_ADRS       (0x90>>1)
#define SYNC_DEV_ADRS      (0x9C>>1)

//#define PLL_REGRD(reg) 		I2cRegReadC(COD_DEV_ADRS, reg, c)
//#define PLL_REGWR(reg, val) I2cRegWriteC(COD_DEV_ADRS, reg, val, c)
//#define PLL_REGRD(reg) 		I2cRegRead(COD_DEV_ADRS, reg,  p_i2c_scl, p_i2c_sda)
//#define PLL_REGWR(reg, val) I2cRegWrite(COD_DEV_ADRS, reg, val,  p_i2c_scl, p_i2c_sda)

int readReg2(unsigned devAdr, unsigned reg, chanend c)
{
    unsigned char data[1] = {0};
    iic_readC(devAdr, reg, data, 1, c, p_i2c_scl, p_i2c_sda);
    return data[0];
}

#define PLL_REGRD(reg) 		readReg2(COD_DEV_ADRS, reg, c)
#define PLL_REGWR(reg, val) {data[0] = val; iic_writeC(COD_DEV_ADRS, reg, data, 1, c, p_i2c_scl, p_i2c_sda);}


/*: CODEC initialisation for Cirrus Logic CS42448 */
void CodecInit(chanend ?c) 
{
    unsigned tmp;
    unsigned char data[1] = {0};

    /* Clock buffers and CODEC out of reset */
#ifdef CODEC_SLAVE
    p_aud_cfg <: 0b1000;
#else
    p_aud_cfg <: 0b1010;
#endif

    /* Power Control Register (Address 02h) */
    /* 0    Power Down                           (PDN)   = 1 Enable, 0 Disable */  
    /* 1:4  Power Down DAC Pairs            (PDN_DACX)   = 1 Enable, 0 Disable */
    /* 5:7  Power Down ADC Pairs            (PDN_ADCX)   = 1 Enable, 0 Disable */
    tmp = 0x01;
    //I2cRegWrite(COD_DEV_ADRS, 0x2, tmp, p_i2c_scl, p_i2c_sda);
    PLL_REGWR(0x2, tmp);

    /* Interface Formats Register (Address 04h)             */
    /* 0    Freeze Controls                    (FREEZE)     = 0,               */
    /* 1    Auxiliary Digital Interface Format (AUX_DIF)    = 0, */
    /* 2:4  DAC Digital Interface Format       (DAC_DIF)    = 010 (Right justified, 24bit) */
    /* 5:7  ADC Digital Interface Format       (ADC_DIF)    = 010 (Rigth justified, 24bit) */
    tmp = 0x49;
    //I2cRegWrite(COD_DEV_ADRS, 0x4, tmp, p_i2c_scl, p_i2c_sda);
    PLL_REGWR(0x4, tmp);
    
    /* ADC Control & DAC De-Emphasis (Address 05h) */
    /* 0   ADC1-2_HPF FREEZE = 0, */
    /* 1   ADC3_HPF FREEZE = 0, */
    /* 2   DAC_DEM = 0, */
    /* 3   ADC1_SINGLE = 1(single ended), */
    /* 4   ADC2_SINGLE = 1, */
    /* 5   ADC3_SINGLE = 1, */
    /* 6   AIN5_MUX = 0, */
    /* 7   AIN6_MUX = 0 */
    tmp = 0x1C;
    //I2cRegWrite(COD_DEV_ADRS, 0x5, tmp, p_i2c_scl, p_i2c_sda);
    PLL_REGWR(0x5, tmp);

    /* Power Control Register (Address 02h) - PDN disable */
    tmp = 0x00;
    //I2cRegWrite(COD_DEV_ADRS, 0x2, tmp, p_i2c_scl, p_i2c_sda);
    PLL_REGWR(0x2, tmp);


}

/* CODEC configuration for sample frequency change for Cirrus Logic CS42448 */
void CodecConfig(unsigned samFreq, unsigned mClk, chanend ?c)
{
    unsigned tmp;
    unsigned char data[1] = {0};
    
    /* Functional Mode (Address 03h) */
    /* 0:1  DAC Functional Mode                    Slave:Auto-detect samp rate      11 */
    /* 2:3  ADC Functional Mode                    Slave:Auto -detect samp rate     11 */
    /*                                             Master: Single                   00 */
    /*                                             Master: Double                   01 */
    /*                                             Master: Quad                     10 */
    /* 4:6  MCLK Frequency                         256/128/64 :                    000 */
    /*                                             512/256/128:                    010 */
    /* 7                                           Reserved                            */
#ifdef CODEC_SLAVE
    tmp = 0b11110000;                                             /* Autodetect */
#else
    if(samFreq < 50000)
    {
        tmp = 0b00000000;
    }
    else if(samFreq < 100000)
    {
        tmp = 0b01010000;
    }
    else
    {
        tmp = 0b10100000;
    }
#endif
    if(mClk < 15000000)
    {
        tmp |= 0;                   // 256/128/64
    }
    else if(mClk < 25000000)
    {
        tmp |= 0b00000100;            // 512/256/128
    }
    else
    {
        printstrln("Err: MCLK currently not supported");
    }

    //I2cRegWrite(COD_DEV_ADRS, 0x3, tmp, p_i2c_scl, p_i2c_sda);
    PLL_REGWR(0x3, tmp);
}

