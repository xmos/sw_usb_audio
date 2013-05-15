#include <xs1.h>
#include <print.h>
#include "devicedefines.h"
#include "i2c.h"
#include "gpio_defines.h"

extern out port p_gpo;
extern out port p_audrst;
extern struct r_i2c i2cPorts; 


void p_gpo_out(unsigned x)
{
    asm("out res[%0], %1"::"r"(p_gpo),"r"(x)); 
}

unsigned p_gpo_peek()
{
    unsigned x;
    asm("peek %0, res[%1]":"=r"(x):"r"(p_gpo));
    return x; 
}


//:codec_init
void AudioHwInit(chanend ?c_codec) 
{
    unsigned x;

    asm("peek %0, res[%1]":"=r"(x):"r"(p_gpo));

    x |= (P_GPIO_5VA_EN | P_GPIO_SS_EN_CTRL);

    asm("out res[%0], %1"::"r"(p_gpo),"r"(x)); 

    return;
}
//:


/* I2C address of CS4392 DAC */
#define DAC_I2C_DEV_ADDR               0x10

/* Mode Control 1 Register - Address 0x01 */
#define DAC_REG_ADDR_MODE_CTRL1        0x01

/* Volume and Mixing Control - Address 0x02 */
#define DAC_REG_ADDR_VOLMIX_CTRL       0x02

/* Channel A Volume Control - Address 0x03 */
#define DAC_REG_ADDR_A_VOL             0x03

/* Channel B Volume Control - Address 0x04 */
#define DAC_REG_ADDR_B_VOL             0x04

/* Mode Control 2 - Address 0x05 */
#define DAC_REG_ADDR_MODE_CTRL2        0x05

#define DAC_REG_MODE_CTRL2_MCLKDIV2    0x02
#define DAC_REG_MODE_CTRL2_FREEZE      0x04
#define DAC_REG_MODE_CTRL2_MUTECAB     0x08
#define DAC_REG_MODE_CTRL2_PDN         0x10
#define DAC_REG_MODE_CTRL2_CPEN        0x20
#define DAC_REG_MODE_CTRL2_INVERTB     0x40
#define DAC_REG_MODE_CTRL2_INVERTA     0x80

/* Mode Control 3 - Address 0x06 */
#define DAC_REG_ADDR_MODE_CTRL3        0x06

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(DAC_I2C_DEV_ADDR, reg, data, 1, i2cPorts);}

unsigned readReg(unsigned devAddr, unsigned reg)
{
    unsigned char data[1] = {0};
    i2c_master_read_reg(devAddr, reg, data, 1, i2cPorts);
    return data[0];
}
 
#define DAC_REGREAD(reg, val)  {i2c_master_read_reg(DAC_I2C_DEV_ADDR, reg, val, 1, i2cPorts);}

//:codec_config
/* Called on a sample frequency change */
/* Configure the CS4392 DAC
 * Note the CS5340 ADC doesn't require any config - it is set to Slave mode in hardware (M0 & M1 pins high)
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, int dsdMode)
{
    timer t;
    unsigned time;
    unsigned tmp;
    int codec_dev_id;
    unsigned char data[] = {0, 0};

    /* Set DAC and ADC in reset */
    p_audrst <: 0;
   
    tmp = p_gpo_peek();
     
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
    p_gpo_out(tmp);

    /* Hold in reset for 2ms while waiting for MCLK to stabilise */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    if(dsdMode)
    {
        p_audrst <: 0b011;
    }
    else
    {
        p_audrst <: 0b111;
    }

    /* Set power down (PDN) bit and Control Port Enable bit in DAC */
    DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL2, DAC_REG_MODE_CTRL2_CPEN | DAC_REG_MODE_CTRL2_PDN);
 
    /* Mode Control 1 
     * 0:1: Functional Mode
     * 2:3: De-emphasis Control
     * 4:6: Digital Interface Formats
     * 7:   Auto-mute
    */
    if(dsdMode)
    {
            DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b00000011);
    }
    else
    {
        if(samFreq < 100000)
        {  
            /* Auto-mute off, i2s, Single-speed */
            DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b00010000);
        }
        else
        {
            /* Auto-mute off, i2s, Double-speed */
            DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b00010010);
        }
    }

    /* Volume and Mixing Control
     * 0:   ATAPI 0
     * 1:   ATAPI 1
     * 2:   ATAPI 2
     * 3:   ATAPI 3
     * 4:   ATAPI 4
     * 5:   Zero Cross
     * 6:   Soft Ramp
     * 7:   A vol = B vol
     */
    DAC_REGWRITE(DAC_REG_ADDR_VOLMIX_CTRL, 0b01101001); 

    /* Channel A/B Volume Control
     * 0:6: Vol0:Vol6 (Attenutation from 0 to -127db)
     * 7:   Mute
     */
    DAC_REGWRITE(DAC_REG_ADDR_A_VOL, 0b00000000);
    DAC_REGWRITE(DAC_REG_ADDR_B_VOL, 0b00000000);

    /* Mode Control 2 
     * 0:1: Reserved
     * 2:   Soft Volume Ramp-up after Reset 
     * 3:   Soft Volume Ramp-down after Reset   
     * 4:   Interperlolation Filter Select (0 fast or 1 slow roll-off)
     * 5:7: Reserved
     */
    DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL2, 0b00000000);

    if(dsdMode) 
    {
     //   IIC_REGWRITE_PCM1795(20, 0b001010000100000);
    }
    else
    {
       // IIC_REGWRITE_PCM1795(20, 0b001010000000000);
    }

#ifdef CODEC_MASTER
#error not currently implemented
#endif 
    
    /* Clear power down bit in the DAC - keep control port enabled for now */
    DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL2, DAC_REG_MODE_CTRL2_CPEN);
 
}
//:
