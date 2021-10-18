#include <xs1.h>
#include <assert.h>
#include <platform.h>
#include <print.h>
#include "xua.h"
#include "i2c_shared.h"
#include "tlv320aic3204.h"
#include "dsd_support.h"

on tile[1] : out port p_gpio = XS1_PORT_8C;

// I2C ports
// I2C is on Tile0
// SCL is on X0D37 - XS1_PORT_1N
// SDA is on X0D38 - XS1_PORT_1O
// on tile[0]: struct r_i2c r_i2c = {PORT_I2C_SCL, PORT_I2C_SDA,};

// struct r_i2c s_i2c = {
//     PORT_I2C_SCL,
//     PORT_I2C_SDA,
//     1000,
// };
on tile [AUDIO_IO_TILE] : struct r_i2c r_i2c = {PORT_I2C};

// CODEC Reset
// extern out port p_codec_reset;
on tile[AUDIO_IO_TILE]: out port p_codec_reset              = PORT_CODEC_RST_N;


// TLV320AIC3204 easy register access defines
// #define AIC3204_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(AIC3204_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}
// #define AIC3204_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(AIC3204_I2C_DEVICE_ADDR, reg, data, 1, r_i2c);}

#define AIC3204_REGREAD(reg, data)  {data[0] = 0xAA; i2c_shared_master_read_reg(r_i2c, AIC3204_I2C_DEVICE_ADDR, reg, data, 1);}
#define AIC3204_REGWRITE(reg, val) {data[0] = val; i2c_shared_master_write_reg(r_i2c, AIC3204_I2C_DEVICE_ADDR, reg, data, 1);}

// CODEC Reset
#define CODEC_RELEASE_RESET      (0x8) // Release codec from

// App PLL setup
#define APP_PLL_CTL_BYPASS       (0)   // 0 = no bypass, 1 = bypass.
#define APP_PLL_CTL_INPUT_SEL    (0)   // 0 = XTAL, 1 = sysPLL
#define APP_PLL_CTL_ENABLE       (1)   // 0 = disabled, 1 = enabled.

// 24MHz in, 24.576MHz out, integer mode
// Found exact solution:   IN  24000000.0, OUT  24576000.0, VCO 2457600000.0, RD  5, FD  512, OD 10, FOD  10
#define APP_PLL_CTL_OD_48        (4)   // Output divider = (OD+1)
#define APP_PLL_CTL_F_48         (511) // FB divider = (F+1)/2
#define APP_PLL_CTL_R_48         (4)   // Ref divider = (R+1)

// 24MHz in, 22.5792MHz out (44.1kHz * 512), frac mode
// Found exact solution:   IN  24000000.0, OUT  22579200.0, VCO 2257920000.0, RD  5, FD  470.400 (m =   2, n =   5), OD  5, FOD   10
#define APP_PLL_CTL_OD_441       (4)   // Output divider = (OD+1)
#define APP_PLL_CTL_F_441        (469) // FB divider = (F+1)/2
#define APP_PLL_CTL_R_441        (4)   // Ref divider = (R+1)

#define APP_PLL_DIV_INPUT_SEL    (1)   // 0 = sysPLL, 1 = app_PLL
#define APP_PLL_DIV_DISABLE      (0)   // 1 = disabled (pin connected to X1D11), 0 = enabled divider output to pin.
#define APP_PLL_DIV_VALUE        (4)   // Divide by N+1 - remember there's a /2 also afterwards for 50/50 duty cycle.

// Fractional divide is M/N
#define APP_PLL_FRAC_EN             (1)   // 0 = disabled (do not use fractional feedback divider), 1 = enabled
#define APP_PLL_FRAC_NPLUS1_CYCLES  (1)   // M value is this reg value + 1.
#define APP_PLL_FRAC_TOTAL_CYCLES   (4)   // N value is this reg value + 1.

// 44.1 kHz
#define APP_PLL_CTL_441  ((APP_PLL_CTL_BYPASS << 29) | (APP_PLL_CTL_INPUT_SEL << 28) | (APP_PLL_CTL_ENABLE << 27) | (APP_PLL_CTL_OD_441 << 23) | (APP_PLL_CTL_F_441 << 8) | APP_PLL_CTL_R_441)
// 48 kHz
#define APP_PLL_CTL_48   ((APP_PLL_CTL_BYPASS << 29) | (APP_PLL_CTL_INPUT_SEL << 28) | (APP_PLL_CTL_ENABLE << 27) | (APP_PLL_CTL_OD_48 << 23) | (APP_PLL_CTL_F_48 << 8) | APP_PLL_CTL_R_48)
#define APP_PLL_DIV      ((APP_PLL_DIV_INPUT_SEL << 31) | (APP_PLL_DIV_DISABLE << 16) | APP_PLL_DIV_VALUE)
#define APP_PLL_FRAC     ((APP_PLL_FRAC_EN << 31) | (APP_PLL_FRAC_NPLUS1_CYCLES << 8) | APP_PLL_FRAC_TOTAL_CYCLES)

void AudioHwInit()
{
    unsigned char data[1] = {0};

    /* Init the i2c module */
    i2c_shared_master_init(r_i2c);

    // take CODEC only out of reset. Is in reset by default - hi-z drives pulldown.
    p_codec_reset <: CODEC_RELEASE_RESET;

    delay_milliseconds(100);

    // Check we can talk to the CODEC
    AIC3204_REGREAD(0, data);
    if (data[0] != 0)
    {
        printstrln("DAC Reg Read Problem?\n");
        printstr("DAC Reg Read Addr 0:"); printintln(data[0]);
    }

    // Set register page to 0
    AIC3204_REGWRITE(AIC3204_PAGE_CTRL, 0x00);

    // Initiate SW reset (PLL is powered off as part of reset)
    AIC3204_REGWRITE(AIC3204_SW_RST, 0x01);

    // Program clock settings

    // Default is CODEC_CLKIN is from MCLK pin. Don't need to change this.
    // Power up NDAC and set to 1
    AIC3204_REGWRITE(AIC3204_NDAC, 0x81);
    // Power up MDAC and set to 4
     AIC3204_REGWRITE(AIC3204_MDAC, 0x84);
    // Power up NADC and set to 1
    AIC3204_REGWRITE(AIC3204_NADC, 0x81);
    // Power up MADC and set to 4
     AIC3204_REGWRITE(AIC3204_MADC, 0x84);
    // Program DOSR = 128
    AIC3204_REGWRITE(AIC3204_DOSR, 0x80);
    // Program AOSR = 128
    AIC3204_REGWRITE(AIC3204_AOSR, 0x80);
    // Set Audio Interface Config: I2S, 24 bits, slave mode, DOUT always driving.
    //   AIC3204_REGWRITE(AIC3204_CODEC_IF, 0x20);
    AIC3204_REGWRITE(AIC3204_CODEC_IF, 0x30);     // 32 bit mode
    // Program the DAC processing block to be used - PRB_P1
    AIC3204_REGWRITE(AIC3204_DAC_SIG_PROC, 0x01);
    // Program the ADC processing block to be used - PRB_R1
    AIC3204_REGWRITE(AIC3204_ADC_SIG_PROC, 0x01);
    // Select Page 1
    AIC3204_REGWRITE(AIC3204_PAGE_CTRL, 0x01);
    // Enable the internal AVDD_LDO:
    AIC3204_REGWRITE(AIC3204_LDO_CTRL, 0x09);
    //
    // Program Analog Blocks
    // ---------------------
    //
    // Disable Internal Crude AVdd in presence of external AVdd supply or before powering up internal AVdd LDO
    AIC3204_REGWRITE(AIC3204_PWR_CFG, 0x08);
    // Enable Master Analog Power Control
    AIC3204_REGWRITE(AIC3204_LDO_CTRL, 0x01);
    // Set Common Mode voltages: Full Chip CM to 0.9V and Output Common Mode for Headphone to 1.65V and HP powered from LDOin @ 3.3V.
    AIC3204_REGWRITE(AIC3204_CM_CTRL, 0x33);
    // Set PowerTune Modes
    // Set the Left & Right DAC PowerTune mode to PTM_P3/4. Use Class-AB driver.
    AIC3204_REGWRITE(AIC3204_PLAY_CFG1, 0x00);
    AIC3204_REGWRITE(AIC3204_PLAY_CFG2, 0x00);
    // Set ADC PowerTune mode PTM_R4.
    AIC3204_REGWRITE(AIC3204_ADC_PTM, 0x00);
    // Set MicPGA startup delay to 3.1ms
    AIC3204_REGWRITE(AIC3204_AN_IN_CHRG, 0x31);
    // Set the REF charging time to 40ms
    AIC3204_REGWRITE(AIC3204_REF_STARTUP, 0x01);
    // HP soft stepping settings for optimal pop performance at power up
    // Rpop used is 6k with N = 6 and soft step = 20usec. This should work with 47uF coupling
    // capacitor. Can try N=5,6 or 7 time constants as well. Trade-off delay vs �pop� sound.
    AIC3204_REGWRITE(AIC3204_HP_START, 0x25);
    // Route Left DAC to HPL
    AIC3204_REGWRITE(AIC3204_HPL_ROUTE, 0x08);
    // Route Right DAC to HPR
    AIC3204_REGWRITE(AIC3204_HPR_ROUTE, 0x08);
    // We are using Line input with low gain for PGA so can use 40k input R but lets stick to 20k for now.
    // Route IN2_L to LEFT_P with 20K input impedance
    AIC3204_REGWRITE(AIC3204_LPGA_P_ROUTE, 0x20);
    // Route IN2_R to LEFT_M with 20K input impedance
    AIC3204_REGWRITE(AIC3204_LPGA_N_ROUTE, 0x20);
    // Route IN1_R to RIGHT_P with 20K input impedance
    AIC3204_REGWRITE(AIC3204_RPGA_P_ROUTE, 0x80);
    // Route IN1_L to RIGHT_M with 20K input impedance
    AIC3204_REGWRITE(AIC3204_RPGA_N_ROUTE, 0x20);
    // Unmute HPL and set gain to 0dB
    AIC3204_REGWRITE(AIC3204_HPL_GAIN, 0x00);
    // Unmute HPR and set gain to 0dB
    AIC3204_REGWRITE(AIC3204_HPR_GAIN, 0x00);
    // Unmute Left MICPGA, Set Gain to 0dB.
    AIC3204_REGWRITE(AIC3204_LPGA_VOL, 0x00);
    // Unmute Right MICPGA, Set Gain to 0dB.
    AIC3204_REGWRITE(AIC3204_RPGA_VOL, 0x00);
    // Power up HPL and HPR drivers
    AIC3204_REGWRITE(AIC3204_OP_PWR_CTRL, 0x30);

    // Wait for 2.5 sec for soft stepping to take effect
    delay_milliseconds(2500);

    //
    // Power Up DAC/ADC
    // ----------------
    //
    // Select Page 0
    AIC3204_REGWRITE(AIC3204_PAGE_CTRL, 0x00);
    // Power up the Left and Right DAC Channels. Route Left data to Left DAC and Right data to Right DAC.
    // DAC Vol control soft step 1 step per DAC word clock.
    AIC3204_REGWRITE(AIC3204_DAC_CH_SET1, 0xd4);
    // Power up Left and Right ADC Channels, ADC vol ctrl soft step 1 step per ADC word clock.
    AIC3204_REGWRITE(AIC3204_ADC_CH_SET, 0xc0);
    // Unmute Left and Right DAC digital volume control
    AIC3204_REGWRITE(AIC3204_DAC_CH_SET2, 0x00);
    // Unmute Left and Right ADC Digital Volume Control.
    AIC3204_REGWRITE(AIC3204_ADC_FGA_MUTE, 0x00);

    delay_milliseconds(1);

    // Set the AppPLL up to output MCLK.
    // Disable the PLL
    write_node_config_reg(tile[AUDIO_IO_TILE], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
    // Enable the PLL to invoke a reset on the appPLL.
    write_node_config_reg(tile[AUDIO_IO_TILE], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
    // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
    write_node_config_reg(tile[AUDIO_IO_TILE], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
    // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
    write_node_config_reg(tile[AUDIO_IO_TILE], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
    write_node_config_reg(tile[AUDIO_IO_TILE], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);

    // Set the fractional divider if used
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM, APP_PLL_FRAC);
    // Wait for PLL output frequency to stabilise due to fractional divider enable
    delay_microseconds(100);
    // Turn on the clock output
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, APP_PLL_DIV);

    delay_milliseconds(1);
}

/* Configures the external audio hardware for the required sample frequency.
 * See gpio.h for I2C helper functions and gpio access
 */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
// unsigned char data[1] = {0};

    // Set the AppPLL up to output MCLK.
    if ((samFreq % 22050) == 0)
    {
        // Disable the PLL
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
        // Enable the PLL to invoke a reset on the appPLL.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
        // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
        // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
    }
    else if ((samFreq % 24000) == 0)
    {
        // Disable the PLL
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_48 & 0xF7FFFFFF));
        // Enable the PLL to invoke a reset on the appPLL.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);
        // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);
        // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_48 & 0xF7FFFFFF));
        write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);
    }

    // Set the fractional divider if used
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM, APP_PLL_FRAC);
    // Wait for PLL output frequency to stabilise due to fractional divider enable
    delay_microseconds(100);
    // Turn on the clock output
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, APP_PLL_DIV);
}

