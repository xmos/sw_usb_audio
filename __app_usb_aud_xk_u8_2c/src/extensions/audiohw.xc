#include <xs1.h>
#include <platform.h>
#include <xs1_su.h>
#include <print.h>
#include "devicedefines.h"
#include "i2c_shared.h"
#include "gpio_defines.h"
#include "gpio_access.h"
#include "interrupt.h"
#include "dsd_support.h"

/* General Purpose Output port - various output lines such as DAC reset, LEDs etc */
on tile[0] : out port p_gpo   = XS1_PORT_32A;

/* Input port for buttons and switch */
on tile[0] : in port p_sw     = XS1_PORT_4D;


#ifndef IAP
/* If IAP not enabled, i2c ports not declared - still needs for DAC config */
on tile [AUDIO_IO_TILE] : struct r_i2c r_i2c = {PORT_I2C_SCL, PORT_I2C_SDA};
#else
extern struct r_i2c r_i2c;
#endif

#if defined(SW_INT_HANDLER) && defined(IAP) && !defined(USB_SEL_A)
#error not currently supported
#endif

#ifdef SW_INT_HANDLER
#ifndef SWITCH_VAL
#define SWITCH_VAL 0b0000
#endif
#pragma select handler
void handle_switch_request(in port p_sw)
{
    unsigned curSwVal;

    asm("in %0, res[%1]":"=r"(curSwVal):"r"(p_sw));
    asm("setd res[%0], %1"::"r"(p_sw),"r"(curSwVal));

    if((curSwVal & 0b1000) != SWITCH_VAL)
    {
        /* Reset U8 device */
        write_node_config_reg(usb_tile, XS1_SU_CFG_RST_MISC_NUM, 1);
    }

}
#endif

#ifdef USB_SEL_A
#define USB_SEL_VAL P_GPIO_USB_SEL1
#else
#define USB_SEL_VAL 0
#endif

//:codec_init
void AudioHwInit(chanend ?c_codec)
{
    unsigned x;
#ifdef SW_INT_HANDLER
    unsigned curSwVal;
    timer t;
    unsigned time;
#endif

    port32A_lock_peek(x);

#ifndef IAP
    /* P_GPIO_VBUS_OUT_EN is pulled up, drive low to disable in non MFi builds */
    x&= ~P_GPIO_VBUS_OUT_EN;
#endif
    x |= (P_GPIO_5VA_EN | P_GPIO_SS_EN_CTRL | USB_SEL_VAL);

    port32A_out_unlock(x);

    /* The 5VA_EN line has a cap on it, wait for it to go high */
    port32A_lock();
    while(1)
    {
        x = peek(p_gpo);
        if((x & P_GPIO_5VA_EN) == P_GPIO_5VA_EN)
            break;
    }
    port32A_unlock();

#ifdef SW_INT_HANDLER
     /* Give some time for button debounce */
    t :> time;
    t when timerafter(time+10000000):> void;

    p_sw :> curSwVal;
    curSwVal = (curSwVal & 0b0111) | SWITCH_VAL; // Ensure we don't miss any switches that happened during reboot

    asm("setc res[%0], %1"::"r"(p_sw),"r"(XS1_SETC_COND_NEQ));
    asm("setd res[%0], %1"::"r"(p_sw),"r"(curSwVal));

    set_interrupt_handler(handle_switch_request, 1, p_sw, 0)
#endif
    return;
}
//:


/* I2C address of CS4392 DAC */
#define DAC_I2C_DEV_ADDR               (0x20>>1)

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

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_shared_master_write_reg(r_i2c, DAC_I2C_DEV_ADDR, reg, data, 1);}

#define DAC_REGREAD(reg, val)  {i2c_shared_master_read_reg(r_i2c, DAC_I2C_DEV_ADDR, reg, val, 1);}

//:codec_config
/* Called on a sample frequency change */
/* Configure the CS4392 DAC
 * Note the CS5340 ADC doesn't require any config - it is set to Slave mode in hardware (M0 & M1 pins high)
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned samRes_DAC, unsigned samRes_ADC)
{
    timer t;
    unsigned time;
    unsigned tmp;
    unsigned char data[] = {0, 0};


    port32A_lock_peek(tmp);

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
    port32A_out_unlock(tmp);

    /* Hold in reset for 2ms while waiting for MCLK to stabilise */
    t :> time;
    time += 200000;
    t when timerafter(time) :> int _;

    /* ADC and DAC out of Reset */
    port32A_lock_peek(tmp);

#if (DSD_CHANS_DAC > 0)
    if(dsdMode)
    {
        /* Set DSD mux line high */
        tmp |= (P_GPIO_DSD_EN);
    }
    else
    {
        tmp &= (~P_GPIO_DSD_EN);
    }
#else
    tmp &= (~P_GPIO_DSD_EN);
#endif

    /* ADC and DAC out of Reset */
    tmp |= (P_GPIO_RST_DAC | P_GPIO_RST_ADC);

    port32A_out_unlock(tmp);

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
#if (DSD_CHANS_DAC > 0)
    if((dsdMode == DSD_MODE_NATIVE) || (dsdMode == DSD_MODE_DOP))
    {
        if(samFreq < 3000000) /* < 3MHz e.g. 2.2822400 MHz */
        {
            /* 64x oversampled DSD with 8 x DSD clock to mclk */
            DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b00100011);
        }
        else
        {
            /* 128x oversampled DSD with 4 x DSD clock to mclk */
            DAC_REGWRITE(DAC_REG_ADDR_MODE_CTRL1, 0b01100011);
        }
    }
    else
#endif
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
