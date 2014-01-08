#include <xs1.h>
#include <xs1.h>
#include <platform.h>
#include <print.h>
#include <stdio.h>

#include "devicedefines.h"
#include "i2c.h"

on tile[0] : out port p_dac_cfg  = XS1_PORT_4C;
on tile[0] : out port p_gpio     = XS1_PORT_32A;
on tile[0] : port p_i2c          = XS1_PORT_4D;

/* Input freq to CS2200 */
#define INPUT_CLOCK_FREQ            (24000000)

#define CS2200_I2C_DEVICE_ADDR      (0b10011100)

#define CS2200_DEVICE_CONFIG_1      0x03
#define CS2200_GLOBAL_CONFIG        0x05
#define CS2200_RATIO_1              0x06
#define CS2200_RATIO_2              0x07
#define CS2200_RATIO_3              0x08
#define CS2200_RATIO_4              0x09
#define CS2200_FUNC_CONFIG_1        0x16
#define CS2200_FUNC_CONFIG_2        0x17

#define CS2200_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS2200_I2C_DEVICE_ADDR, reg, data, 1, p_i2c);}
#define CS2200_REGREAD(reg, val)  {data[0] = 0xAA; i2c_master_read_reg(CS2200_I2C_DEVICE_ADDR, reg, val, 1, p_i2c);}
//:codec_init

/* Setup PLL multiplier */
void PllMult(unsigned inputClk, unsigned outputClk)
{
    unsigned char data[] = {0, 0};
    float mult = 0;
    unsigned umult = 0;

    mult = (float) ((float)outputClk / (float) inputClk) * ((float)1048576);/* 2 ^ 20 */

    umult = (unsigned) mult;

    /* Multiplier is translated to 20.12 format */
    CS2200_REGWRITE(CS2200_RATIO_4, (umult) & 0xFF);
    CS2200_REGWRITE(CS2200_RATIO_3, (umult >> 8) & 0xFF);
    CS2200_REGWRITE(CS2200_RATIO_2, (umult >> 16) & 0xFF);
    CS2200_REGWRITE(CS2200_RATIO_1, (umult>>24));
}

void AudioHwInit(chanend ?c_codec)
{
    unsigned char data[] = {0, 0};

    i2c_master_init(p_i2c);

    CS2200_REGWRITE(CS2200_FUNC_CONFIG_1, 0b00001000);
    CS2200_REGWRITE(CS2200_FUNC_CONFIG_2, 0b00010000);
    CS2200_REGWRITE(CS2200_DEVICE_CONFIG_1, 0b00000001);
    CS2200_REGWRITE(CS2200_GLOBAL_CONFIG, 0b00000001);
    CS2200_REGWRITE(CS2200_GLOBAL_CONFIG, 0b00000001);

    PllMult(INPUT_CLOCK_FREQ, DEFAULT_MCLK_FREQ);

    return;
}
//:

//:codec_config
/* Called on a sample frequency change */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode)
{
    timer t;
    unsigned time;
    unsigned tmp;
    int codec_dev_id;

    /* Configure master clock to required rate */
    PllMult(INPUT_CLOCK_FREQ, mClk);

}
//:
