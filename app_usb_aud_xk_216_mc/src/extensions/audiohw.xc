#include <xs1.h>

#include <assert.h>
#include "devicedefines.h"
#include <platform.h>
#include "gpio_access.h"
#include "i2c_shared.h"
#include "cs4384.h"
#include "cs5368.h"
#include "cs2100.h"
#include "print.h"
#include "dsd_support.h"

/* The number of timer ticks to wait for the audio PLL to lock */
/* CS2100 lists typical lock time as 100 * input period */
#define     AUDIO_PLL_LOCK_DELAY     (40000000)

#if defined(SPDIF_RX) || defined(ADAT_RX)
#define USE_FRACTIONAL_N 1
#endif

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

#ifdef USE_FRACTIONAL_N

#if !(defined(SPDIF_RX) || defined(ADAT_RX))
/* Choose a frequency the xcore can easily generate internally */
#define PLL_SYNC_FREQ 1000000
#else
#define PLL_SYNC_FREQ 300
#endif

#define CS2100_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}
#define CS2100_REGREAD_ASSERT(reg, data, expected)  {data[0] = 0xAA; i2c_master_read_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c); assert(data[0] == expected);}
#define CS2100_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(CS2100_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}

/* Init of CS2100 */
void PllInit(void)
{
    unsigned char data[1] = {0};

#if XCORE_200_MC_AUDIO_HW_VERSION < 2
    /* Enable init */
    CS2100_REGWRITE(CS2100_DEVICE_CONFIG_1, 0x05);
#else
    CS2100_REGWRITE(CS2100_DEVICE_CONFIG_1, 0x07);
#endif
    CS2100_REGWRITE(CS2100_GLOBAL_CONFIG, 0x01);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_1, 0x08);
    CS2100_REGWRITE(CS2100_FUNC_CONFIG_2, 0x00); //0x10 for always gen clock even when unlocked

    /* Read back and check */
#if XCORE_200_MC_AUDIO_HW_VERSION < 2
    CS2100_REGREAD_ASSERT(CS2100_DEVICE_CONFIG_1, data, 0x05);
#else
    CS2100_REGREAD_ASSERT(CS2100_DEVICE_CONFIG_1, data, 0x07);
#endif
    CS2100_REGREAD_ASSERT(CS2100_GLOBAL_CONFIG, data, 0x01);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_1, data, 0x08);
    CS2100_REGREAD_ASSERT(CS2100_FUNC_CONFIG_2, data, 0x00);
}

/* Setup PLL multiplier */
void PllMult(unsigned output, unsigned ref)
{
    unsigned char data[1] = {0};

    /* PLL expects 12:20 format, convert output and ref to 12:20 */
    /* Shift up the dividend by 12 to retain format... */
    unsigned mult = (unsigned) ((((unsigned long long)output) << 32) / (((unsigned long long)ref) << 20));

    CS2100_REGWRITE(CS2100_RATIO_1, (mult >> 24) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_2, (mult >> 16) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_3, (mult >> 8) & 0xFF);
    CS2100_REGWRITE(CS2100_RATIO_4, (mult & 0xFF));

	/* Read back and check */
    CS2100_REGREAD_ASSERT(CS2100_RATIO_1, data, ((mult >> 24) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_2, data, ((mult >> 16) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_3, data, ((mult >> 8) & 0xFF));
    CS2100_REGREAD_ASSERT(CS2100_RATIO_4, data, (mult & 0xFF));
}
#endif

#if !(defined(SPDIF_RX) || defined(ADAT_RX)) && defined(USE_FRACTIONAL_N)
on tile[AUDIO_IO_TILE] : out port p_pll_clk = PORT_PLL_REF;
on tile[AUDIO_IO_TILE] : clock clk_pll_sync = XS1_CLKBLK_5;
#endif

void wait_us(int microseconds)
{
    timer t;
    unsigned time;

    t :> time;
    t when timerafter(time + (microseconds * 100)) :> void;
}

void AudioHwInit(chanend ?c_codec)
{
#if !(defined(SPDIF_RX) || defined(ADAT_RX)) && defined(USE_FRACTIONAL_N)
    /* Output a fixed sync clock to the pll */
    configure_clock_rate(clk_pll_sync, 100, 100/(PLL_SYNC_FREQ/1000000));
    configure_port_clock_output(p_pll_clk, clk_pll_sync);
    start_clock(clk_pll_sync);
#endif

    /* Init the i2c module */
    i2c_shared_master_init(r_i2c);

    /* Assert reset to ADC and DAC */
    set_gpio(P_GPIO_DAC_RST_N, 0);
    set_gpio(P_GPIO_ADC_RST_N, 0);

    /* 0b11 : USB B */
    /* 0b01 : Lightning */
    /* 0b10 : USB A */
#ifdef USB_SEL_A
    set_gpio(P_GPIO_USB_SEL0, 0);
    set_gpio(P_GPIO_USB_SEL1, 1);
#else
    set_gpio(P_GPIO_USB_SEL0, 1);
    set_gpio(P_GPIO_USB_SEL1, 1);
#endif

#ifdef USE_FRACTIONAL_N
    /* If we have any digital input then use the external PLL - selected via MUX */
    set_gpio(P_GPIO_PLL_SEL, 1);

     /* Initialise external PLL */
    PllInit();
#endif

#ifdef IAP
    /* Enable VBUS output */
    set_gpio(P_GPIO_VBUS_EN, 1);
#endif
}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
	unsigned char data[1] = {0};

    /* Put ADC and DAC into reset */
	set_gpio(P_GPIO_ADC_RST_N, 0);
	set_gpio(P_GPIO_DAC_RST_N, 0);

    /* Set master clock select appropriately */
#if defined(USE_FRACTIONAL_N)
    /* Configure external fractional-n clock multiplier for 300Hz -> mClkFreq */
    PllMult(mClk, PLL_SYNC_FREQ);
#endif
    /* Allow some time for mclk to lock and MCLK to stabilise - this is important to avoid glitches at start of stream */
    {
        timer t;
        unsigned time;
        t :> time;
        t when timerafter(time+AUDIO_PLL_LOCK_DELAY) :> void;
    }

#if defined(USE_FRACTIONAL_N)
    while(1)
    {
        /* Read Unlock Indicator in PLL as sanity check... */
        CS2100_REGREAD(CS2100_DEVICE_CONTROL, data);
        if(!(data[0] & 0x80))
        {
            break;
        }
    }
#else
    if (mClk == MCLK_441)
    {
        set_gpio(P_GPIO_MCLK_FSEL, 0);
    }
    else
    {
        set_gpio(P_GPIO_MCLK_FSEL, 1); //mClk = MCLK_48
    }

    /* Allow MCLK to settle */
    wait_us(20000);
#endif

#if 1
    if((dsdMode == DSD_MODE_NATIVE) || (dsdMode == DSD_MODE_DOP))
    {
        /* Enable DSD 8ch out mode on mux */
        //set_gpio(p_adrst_cksel_dsd, P_DSD_MODE, 1);

        /* DAC out out reset, note ADC left in reset in for DSD mode */
        set_gpio(P_GPIO_DAC_RST_N, 1);

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
        set_gpio(P_GPIO_DSD_MODE, 0);

        /* Take ADC out of reset */
        set_gpio(P_GPIO_ADC_RST_N, 1);

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

#ifdef CODEC_MASTER
        /* Allow some time for clocks from ADC to become stable */
        wait_us(500);
#endif

        /* Configure DAC with PCM values. Note 2 writes to mode control to enable/disable freeze/power down */
        set_gpio(P_GPIO_DAC_RST_N, 1);//De-assert DAC reset

        wait_us(500);

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
        DAC_REGWRITE(CS4384_PCM_CTRL, 0b11000011);
#else
        /* PCM Control (Address: 0x03) */
        /* bit[7:4] : Digital Interface Format (DIF) : 0b0001 for I2S up to 24bit
         * bit[3:2] : Reserved
         * bit[1:0] : Functional Mode (FM) : 0x00 - single-speed mode (4-50kHz)
         *                                 : 0x01 - double-speed mode (50-100kHz)
         *                                 : 0x10 - quad-speed mode (100-200kHz)
         *                                 : 0x11 - auto-speed detect (32 to 200kHz)
         *                                 (note, some Mclk/SR ratios not supported in auto)
         *
         */
        unsigned char regVal = 0;
        if(samFreq < 50000)
            regVal = 0b00010100;
        else if(samFreq < 100000)
            regVal = 0b00010101;
        else //if(samFreq < 200000)
            regVal = 0b00010110;

        DAC_REGWRITE(CS4384_PCM_CTRL, regVal);
#endif

        /* Mode Control 1 (Address: 0x02) */
        /* bit[7] : Control Port Enable (CPEN)     : Set to 1 for enable
         * bit[6] : Freeze controls (FREEZE)       : Set to 0 for freeze
         * bit[5] : PCM/DSD Selection (DSD/PCM)    : Set to 0 for PCM
         * bit[4:1] : DAC Pair Disable (DACx_DIS)  : All Dac Pairs enabled
         * bit[0] : Power Down (PDN)               : Not powered down
         */
        DAC_REGWRITE(CS4384_MODE_CTRL, 0b10000000);
    }
#endif
    return;
}
//:
