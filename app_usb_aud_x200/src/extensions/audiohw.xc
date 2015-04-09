#include <xs1.h>

#define I2C_COMBINE_SCL_SDA 1
#include "devicedefines.h"
#include <platform.h>
#include "gpio.h"
#include "i2c_shared.h"
#include "p_gpio_defines.h"
#include "cs4384.h"
#include "cs5368.h"
#include "print.h"
#include "dsd_support.h"

on tile[0] : out port p_gpio = XS1_PORT_8C;

#ifndef IAP
/* If IAP not enabled, i2c ports not declared - still needs for DAC config */
on tile [0] : struct r_i2c r_i2c = {XS1_PORT_4A};
#else
extern struct r_i2c r_i2c;
#endif

#define DAC_REGWRITE(reg, val) {data[0] = val; i2c_shared_master_write_reg(r_i2c, CS4384_I2C_ADDR, reg, data, 1);}
#define DAC_REGREAD(reg, val)  {i2c_shared_master_read_reg(r_i2c, CS4384_I2C_ADDR, reg, val, 1);}
#define ADC_REGWRITE(reg, val) {data[0] = val; i2c_shared_master_write_reg(r_i2c, CS5368_I2C_ADDR, reg, data, 1);}


void AudioHwInit(chanend ?c_codec)
{
    /* 0b11 : USB B */
    /* 0b10 : Lightning */
    set_gpio(p_gpio, P_GPIO_USB_SEL0, 1);
    set_gpio(p_gpio, P_GPIO_USB_SEL1, 1);

#ifdef IAP
    set_gpio(p_gpio, P_GPIO_VBUS_EN, 1);
#endif

    /* Init the i2c module */
    i2c_shared_master_init(r_i2c);

    /* Assert reset to ADC and DAC */
    set_gpio(p_gpio, P_DAC_RST_N, 0);
    set_gpio(p_gpio, P_ADC_RST_N, 0);
}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
	unsigned char data[1] = {0};

    /* Put ADC and DAC into reset */
	set_gpio(p_gpio, P_GPIO_DAC_RST_N, 0);
	set_gpio(p_gpio, P_GPIO_ADC_RST_N, 0);

    /* Set master clock select appropriately */
    if (mClk == MCLK_441)
    {
        set_gpio(p_gpio, P_GPIO_MCLK_FSEL, 0);
    }
    else
    {
        set_gpio(p_gpio, P_GPIO_MCLK_FSEL, 1); //mClk = MCLK_48
    }

    /* Allow MCLK to settle */
    wait_us(2000);

    if((dsdMode == DSD_MODE_NATIVE) || (dsdMode == DSD_MODE_DOP))
    {
        /* Enable DSD 8ch out mode on mux */
        //set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 1);

        /* DAC out out reset, note ADC left in reset in for DSD mode */
        //set_gpio(p_adrst_cksel_dsd, P_DAC_RST_N, 1);

        /* Configure DAC values required for DSD mode */

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 1 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 1 for DSD
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0xe1);

        if (samFreq > 3000000)
        {
            /* DSD128 */
            /* DSD Control (Address: 0x04) */
            /* bit[7:5] : DSD Digital Inteface Format (DSD_DIF) : 128x over samples with 4x MCLK
             * bit[4] : Direct DSD Conversion: Set to 0, data sent to DSD processor
             * bit[3] : Static DSD detect : 1 for enabled
             * bit[2] : Invalid DSD Detect : 1 for enabled
             * bit[1] : DSD Phase Modulation Mode Select
             * bit[0] : DSD Phase Modulation Enable
             */
            DAC_REGWRITE(CS4384_DSD_CTRL, 0b11001100);
            //set_led_array(LED_SQUARE_BIG);
        }
        else
        {
            /* DSD64 */
            /* DSD Control (Address: 0x04) */
            /* bit[7:5] : DSD Digital Inteface Format (DSD_DIF) : 64x over samples with 8x MCLK
             * bit[4] : Direct DSD Conversion: Set to 0, data sent to DSD processor
             * bit[3] : Static DSD detect : 1 for enabled
             * bit[2] : Invalid DSD Detect : 1 for enabled
             * bit[1] : DSD Phase Modulation Mode Select
             * bit[0] : DSD Phase Modulation Enable
             */
            DAC_REGWRITE(CS4384_DSD_CTRL, 0b01001100);
            //set_led_array(LED_SQUARE_SML);
        }

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 0 for not freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 1 for DSD
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Power down disabled
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0xA0);

        /* Note: ADC kept in reset, no config sent. DSD mode is output only 0*/
    }
    else
    {
        /* dsdMode == 0 */
        /* Set MUX to PCM mode (muxes ADC I2S data lines) */
        set_gpio(p_gpio, P_GPIO_DSD_MODE, 0);

        /* Configure DAC with PCM values. Note 2 writes to mode control to enable/disable freeze/power down */
        set_gpio(p_gpio, P_GPIO_DAC_RST_N, 1);//De-assert DAC reset

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 1 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 0 for PCM
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0b11000001);

#ifdef I2S_MODE_TDM
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b1100 for TDM
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x11 for auto-speed detect (32 to 200kHz)
        */
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b11000111);
#else
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b0001 for I2S up to 24bit
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x11 for auto-speed detect (32 to 200kHz)
        */
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b00010111);
#endif

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 0 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 0 for PCM
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Not powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0b10000000);

        /* Take ADC out of reset */
        set_gpio(p_gpio, P_GPIO_ADC_RST_N, 1);

        {
            unsigned dif = 0, mode = 0;
#ifdef I2S_MODE_TDM
            dif = 0x02;   /* TDM */
#else
            dif = 0x01;   /* I2S */
#endif

#ifdef CODEC_MASTER
            /* Note, only the ADC device supports being I2S master.
             * Set ADC as master and run DAC as slave */
            if(samFreq < 54000)
                mode = 0x00;     /* Single-speed Mode Master */
            else if(samFreq < 108000)
                mode = 0x01;     /* Double-speed Mode Master */
            else if(samFreq < 216000)
                mode = 0x02;     /* Quad-speed Mode Master */
#else
            mode = 0x03;    /* Slave mode all speeds */
#endif

            /* Reg 0x01: (GCTL) Global Mode Control Register */
            /* Bit[7]: CP-EN: Manages control-port mode
            * Bit[6]: CLKMODE: Setting puts part in 384x mode
            * Bit[5:4]: MDIV[1:0]: Set to 01 for /2
            * Bit[3:2]: DIF[1:0]: Data Format: 0x01 for I2S, 0x02 for TDM
            * Bit[1:0]: MODE[1:0]: Mode: 0x11 for slave mode
            */
            ADC_REGWRITE(CS5368_GCTL_MDE, 0b10010000 | (dif << 2) | mode);
        }

        /* Reg 0x06: (PDN) Power Down Register */
        /* Bit[7:6]: Reserved
         * Bit[5]: PDN-BG: When set, this bit powers-own the bandgap reference
         * Bit[4]: PDM-OSC: Controls power to internal oscillator core
         * Bit[3:0]: PDN: When any bit is set all clocks going to that channel pair are turned off
         */
        ADC_REGWRITE(CS5368_PWR_DN, 0b00000000);

        /* Illuminate LEDs based on sample-rate */
        if (samFreq > 192000)
        {
            //set_led_array(LED_ALL_ON);
        }
        else if (samFreq > 96000)
        {
            //set_led_array(LED_ROW_3);
        }
        else if (samFreq > 48000)
        {
            //set_led_array(LED_ROW_2);
        }
        else
        {
            //set_led_array(LED_ROW_1);
        }
    }

    return;
}
//:
