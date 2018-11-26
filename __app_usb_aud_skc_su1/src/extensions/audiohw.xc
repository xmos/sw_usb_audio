#include <xs1.h>
#include <xs1.h>
#include <platform.h>

#include "devicedefines.h"
#include "i2c.h"
#include "p_gpio.h"
#include "p_gpio_defines.h"

on tile[0] : out port p_gpio = XS1_PORT_4C;
on tile[0] : struct r_i2c p_i2c       = {XS1_PORT_4D};

//:codec_init
void AudioHwInit(chanend ?c_codec)
{
    i2c_master_init(p_i2c);

    /* Enable SPDIF output (disables SPI flash) */
    p_gpio <: 1;

    return;
}
//:


/* S1 Board uses I2C configured CODEC */
#define CODEC1_I2C_DEVICE_ADDR       (0x90>>1)
#define CODEC2_I2C_DEVICE_ADDR       (0x92>>1)

#define CODEC_DEV_ID_ADDR           0x01
#define CODEC_PWR_CTRL_ADDR         0x02
#define CODEC_MODE_CTRL_ADDR        0x03
#define CODEC_ADC_DAC_CTRL_ADDR     0x04
#define CODEC_TRAN_CTRL_ADDR        0x05
#define CODEC_MUTE_CTRL_ADDR        0x06
#define CODEC_DACA_VOL_ADDR         0x07
#define CODEC_DACB_VOL_ADDR         0x08

#define IIC_REGWRITE_1(reg, val) {data[0] = val; i2c_master_write_reg(CODEC1_I2C_DEVICE_ADDR, reg, data, 1, p_i2c);}
#define IIC_REGWRITE_2(reg, val) {data[0] = val; i2c_master_write_reg(CODEC2_I2C_DEVICE_ADDR, reg, data, 1, p_i2c);}

/* Write to both CODECs */
#define IIC_REGWRITE(reg, val) {IIC_REGWRITE_1(reg, val);IIC_REGWRITE_2(reg,val);}
#define IIC_REGREAD(reg, val)  {i2c_master_read_reg(CODEC1_I2C_DEVICE_ADDR, reg, val, 1, p_i2c);}


//:codec_config
/* Called on a sample frequency change */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned samRes_DAC, unsigned samRes_ADC)
{
    timer t;
    unsigned time;
    unsigned tmp;
    int codec_dev_id;
    unsigned char data[] = {0, 0};

    /* See whats on the GP out port */
    tmp = p_gpio_peek();

    /* Set CODEC in reset */
    tmp &= ~P_GPIO_COD_RST_N;

    /* Set master clock select appropriately */
    if ((samFreq % 22050) == 0)
    {
        tmp &= ~P_GPIO_MCLK_SEL;
    }
    else //if((samFreq % 24000) == 0)
    {
        tmp |= P_GPIO_MCLK_SEL;
    }

    /* Output to port */
    p_gpio_out(tmp);

    /* Hold in reset for 2ms while waiting for MCLK to stabilise */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* CODEC out of reset */
    tmp |= P_GPIO_COD_RST_N;
    p_gpio_out(tmp);

    /* Set power down bit in the CODEC over I2C */
    IIC_REGWRITE(CODEC_DEV_ID_ADDR, 0x01);

    /* Read CODEC device ID to make sure everything is OK */
    //IIC_REGREAD(CODEC_DEV_ID_ADDR, data);

    //codec_dev_id = data[0];
    //if (((codec_dev_id & 0xF0) >> 4) != 0xC) {
        //printstr("Unexpected CODEC Device ID, expected 0xC, got ");
        //printhex(codec_dev_id);
        //assert(0); // Throw an error
    //}

    /* Now set all registers as we want them :
    Mode Control Reg: */
#ifndef CODEC_MASTER
    /*
    Set FM[1:0] as 11. This sets Slave mode.
    Set MCLK_FREQ[2:0] as 010. This sets MCLK to 512Fs in Single, 256Fs in Double and 128Fs in Quad Speed Modes.
    This means 24.576MHz for 48k and 22.5792MHz for 44.1k.
    Set Popguard Transient Control.
    So, write 0x35. */
    IIC_REGWRITE(CODEC_MODE_CTRL_ADDR,    0x35);
#else

    /* In master mode (i.e. Xcore is I2S slave) to avoid contention configure one CODEC as master one
     * the other as slave */

    /*
    Set FM[1:0] as 11. This sets Slave mode.
    Set MCLK_FREQ[2:0] as 010. This sets MCLK to 512Fs in Single, 256Fs in Double and 128Fs in Quad Speed Modes.
    This means 24.576MHz for 48k and 22.5792MHz for 44.1k.
    Set Popguard Transient Control.
    So, write 0x35. */
    IIC_REGWRITE_1(CODEC_MODE_CTRL_ADDR,    0x35);

    /* Set FM[1:0] Based on Single/Double/Quad mode
    Set MCLK_FREQ[2:0] as 010. This sets MCLK to 512Fs in Single, 256Fs in Double and 128Fs in Quad Speed Modes.
    This means 24.576MHz for 48k and 22.5792MHz for 44.1k.
    Set Popguard Transient Control.*/

    {
        unsigned char val = 0b0101;

        if(samFreq < 54000)
        {
            // | with 0..
        }
        else if(samFreq < 108000)
        {
            val |= 0b00100000;
        }
        else
        {
            val |= 0b00100000;
        }
        IIC_REGWRITE_2(CODEC_MODE_CTRL_ADDR, val);
    }

#endif

    /* ADC & DAC Control Reg:
       Leave HPF for ADC inputs continuously running.
       Digital Loopback: OFF
       DAC Digital Interface Format: I2S
       ADC Digital Interface Format: I2S
       So, write 0x09. */
    IIC_REGWRITE(CODEC_ADC_DAC_CTRL_ADDR, 0x09);

    /* Transition Control Reg:
       No De-emphasis. Don't invert any channels. Independent vol controls. Soft Ramp and Zero Cross enabled.*/
    IIC_REGWRITE(CODEC_TRAN_CTRL_ADDR,    0x60);

    /* Mute Control Reg: Turn off AUTO_MUTE */
    IIC_REGWRITE(CODEC_MUTE_CTRL_ADDR,    0x00);

    /* DAC Chan A Volume Reg:
       We don't require vol control so write 0x00 (0dB) */
    IIC_REGWRITE(CODEC_DACA_VOL_ADDR,     0x00);

    /* DAC Chan B Volume Reg:
       We don't require vol control so write 0x00 (0dB)  */
    IIC_REGWRITE(CODEC_DACB_VOL_ADDR,     0x00);

    /* Clear power down bit in the CODEC over I2C */
    IIC_REGWRITE(CODEC_PWR_CTRL_ADDR, 0x00);
}
//:
