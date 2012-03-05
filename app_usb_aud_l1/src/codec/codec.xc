#include <xs1.h>
#include <print.h>
#include "port32A.h"
#include "devicedefines.h"

//:codec_init
void CodecInit(chanend ?c_codec) 
{
    return;
}
//:

#ifdef BOARD_S1
/* S1 Board uses I2C configured CODEC */
#include "i2c.h"
#define CODEC_I2C_DEVICE_ADDR       0x90
#define CODEC_DEV_ID_ADDR           0x01
#define CODEC_PWR_CTRL_ADDR         0x02
#define CODEC_MODE_CTRL_ADDR        0x03
#define CODEC_ADC_DAC_CTRL_ADDR     0x04
#define CODEC_TRAN_CTRL_ADDR        0x05
#define CODEC_MUTE_CTRL_ADDR        0x06
#define CODEC_DACA_VOL_ADDR         0x07
#define CODEC_DACB_VOL_ADDR         0x08
extern port p_i2c_sda;
extern port p_i2c_scl;
#endif

//:codec_config
void CodecConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec)
{
    timer t;
    unsigned time;
    unsigned portVal;
    unsigned tmp;

#ifdef BOARD_S1
    int codec_dev_id;

    /* See whats on the GP out port */
    tmp = port32A_peek();
    
    /* Set CODEC in reset */
    tmp &= ~P32A_COD_RST_N;
    
    /* Set master clock select appropriately */
    if ((samFreq % 22050) == 0) 
    {
        tmp &= ~P32A_MCLK_SEL;
    }
    else //if((samFreq % 24000) == 0) 
    {
        tmp |= P32A_MCLK_SEL;
    }
    //else {
      //  assert(0); // Throw an error
    //}
    /* Output to port */  
    port32A_out(tmp);

    /* Hold in reset for 2ms while waiting for MCLK to stabilise */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* CODEC out of reset */
    tmp |= P32A_COD_RST_N;
    port32A_out(tmp);
    
    /* Set power down bit in the CODEC over I2C */
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_PWR_CTRL_ADDR, 0x01, p_i2c_scl, p_i2c_sda);
    
    /* Read CODEC device ID to make sure everything is OK */
    codec_dev_id = I2cRegRead(CODEC_I2C_DEVICE_ADDR, CODEC_DEV_ID_ADDR, p_i2c_scl, p_i2c_sda);
    
    if (((codec_dev_id & 0xF0) >> 4) != 0xC) {
        printstr("Unexpected CODEC Device ID, expected 0xC, got ");
        printhex(codec_dev_id);
        //assert(0); // Throw an error
    }
    
    /* Now set all registers as we want them :    
    
    Mode Control Reg:
    Set FM[1:0] as 11. This sets Slave mode.
    Set MCLK_FREQ[2:0] as 010. This sets MCLK to 512Fs in Single, 256Fs in Double and 128Fs in Quad Speed Modes.
    This means 24.576MHz for 48k and 22.5792MHz for 44.1k.
    Set Popguard Transient Control.
    So, write 0x35.

    ADC & DAC Control Reg:
    Leave HPF for ADC inputs continuously running.
    Digital Loopback: OFF
    DAC Digital Interface Format: I2S
    ADC Digital Interface Format: I2S
    So, write 0x09.

    Transition Control Reg:
    No De-emphasis. Don't invert any channels. Independent vol controls. Soft Ramp and Zero Cross enabled.
    So, write 0x60.

    Mute Control Reg:
    Turn off AUTO_MUTE
    So, write 0x00.

    DAC Chan A Volume Reg:
    We don't require vol control so write 0x00 (0dB)

    DAC Chan B Volume Reg:
    We don't require vol control so write 0x00 (0dB)  */
    
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_MODE_CTRL_ADDR,    0x35, p_i2c_scl, p_i2c_sda);
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_ADC_DAC_CTRL_ADDR, 0x09, p_i2c_scl, p_i2c_sda);
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_TRAN_CTRL_ADDR,    0x60, p_i2c_scl, p_i2c_sda);
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_MUTE_CTRL_ADDR,    0x00, p_i2c_scl, p_i2c_sda);
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_DACA_VOL_ADDR,     0x00, p_i2c_scl, p_i2c_sda);
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_DACB_VOL_ADDR,     0x00, p_i2c_scl, p_i2c_sda);

    /* Clear power down bit in the CODEC over I2C */
    I2cRegWrite(CODEC_I2C_DEVICE_ADDR, CODEC_PWR_CTRL_ADDR, 0x00, p_i2c_scl, p_i2c_sda);
#else
    /* L1 Board */
    /* Put codec in reset and set master clock select appropriately */
    if ((samFreq % 22050) == 0)
    {
        portVal = P32A_USB_RST;
    }
    else if((samFreq % 24000) == 0)
    {
        portVal = (P32A_USB_RST | P32A_CLK_SEL);
    }
    else
    {
        if (samFreq == 1234)
          return;
        printintln(samFreq);
        printstr("Unrecognised sample freq in ConfigCodec\n");
    }

    tmp = port32A_peek();
    tmp &= (P32A_LED_A | P32A_LED_B);
    port32A_out(portVal | tmp);

    /* Hold in reset for 2ms */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* Codec out of reset */
    portVal |= P32A_COD_RST;
    tmp = port32A_peek();
    tmp &= (P32A_LED_A | P32A_LED_B);
    port32A_out(portVal | tmp);
#endif
}
//:
