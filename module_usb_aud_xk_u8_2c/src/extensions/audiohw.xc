#include <xs1.h>
#include <platform.h>
#include <xs1_su.h>
#include "devicedefines.h"
#include "i2c.h"
#include "gpio_defines.h"
#include "interrupt.h"

extern in port p_sw;

extern out port p_gpo;
extern out port p_audrst;
extern struct r_i2c i2cPorts; 


#define XS1_SU_PERIPH_USB_ID 1

#ifdef SW_INT_HANDLER
#pragma select handler
void handle_switch_request(in port p_sw)
{
    unsigned curSwVal;

    asm("in %0, res[%1]":"=r"(curSwVal):"r"(p_sw));
    asm("setd res[%0], %1"::"r"(p_sw),"r"(curSwVal));
    
    if((curSwVal & 3) != SWITCH_VAL)
    {
        /* Ideally we would reset SU1 here but then we loose power to the xcore and therefore the DFU flag */
        /* Disable USB and issue reset to xcore only - not analogue chip */
        //write_node_config_reg(usb_tile, XS1_SU_CFG_RST_MISC_NUM,0b10);
        write_node_config_reg(usb_tile, XS1_SU_CFG_RST_MISC_NUM,1);
    }

}
#endif

#define PORT32A_PEEK(X) {asm volatile("peek %0, res[%1]":"=r"(X):"r"(XS1_PORT_32A));} 
#define PORT32A_OUT(X)  {asm volatile("out res[%0], %1"::"r"(XS1_PORT_32A),"r"(X));}
//:codec_init
void AudioHwInit(chanend ?c_codec) 
{
    unsigned x;
    unsigned curSwVal;
    timer t;
    unsigned time;
    int count = 0;

    x = peek(p_gpo);
    
    x |= (P_GPIO_5VA_EN | P_GPIO_SS_EN_CTRL);

    PORT32A_OUT(x);

    /* The 5VA_EN line has a cap on it, wait for it to go high */
    while(1)
    {
        PORT32A_PEEK(x);
        if((x & P_GPIO_5VA_EN) == P_GPIO_5VA_EN)
            break;
    }
    
#ifdef SW_INT_HANDLER
     /* Give some time for button debounce */
    t :> time;
    t when timerafter(time+10000000):> void;

    p_sw :> curSwVal;
    
    asm("setc res[%0], %1"::"r"(p_sw),"r"(XS1_SETC_COND_NEQ));
    asm("setd res[%0], %1"::"r"(p_sw),"r"(curSwVal));

    set_interrupt_handler(handle_switch_request, 200, 1, p_sw, 0)
#endif
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

    PORT32A_PEEK(tmp);
      
    /* Put DAC and ADC into reset */  
    tmp &= (~P_GPIO_RST_DAC);
    tmp &= (~P_GPIO_RST_ADC);
   
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
    PORT32A_OUT(tmp);

    /* Hold in reset for 2ms while waiting for MCLK to stabilise */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* ADC and DAC out of Reset */
    PORT32A_PEEK(tmp);

    if(dsdMode)
    {
        //Set DSD mux line high     
        tmp |= (P_GPIO_DSD_EN);
    }
    else
    {
        tmp &= (~P_GPIO_DSD_EN);
    }

    tmp |= (P_GPIO_RST_DAC | P_GPIO_RST_ADC);
    
    PORT32A_OUT(tmp);

    
    /* Give the DAC a little time to settle down after reset */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;
   
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
        DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b00100011);
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
    DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL3, 0b00000000);


#ifdef CODEC_MASTER
#error not currently implemented
#endif 
    
    /* Clear power down bit in the DAC - keep control port enabled for now */
    DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL2, DAC_REG_MODE_CTRL2_CPEN);
 
}
//:
