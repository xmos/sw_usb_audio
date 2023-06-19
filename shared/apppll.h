#include <platform.h>
#include <stdint.h>

//Found solution: IN 24.000MHz, OUT 49.151786MHz, VCO 3145.71MHz, RD 1, FD 131.071 (m = 1, n = 14), OD 8, FOD 2, ERR -4.36ppm
// Measure: 100Hz-40kHz: ~7ps
// 100Hz-1MHz: 70ps.
// 100Hz high pass: 118ps.
#define APP_PLL_CTL_49M  0x0B808200
#define APP_PLL_DIV_49M  0x80000001
#define APP_PLL_FRAC_49M 0x8000000D

//Found solution: IN 24.000MHz, OUT 45.157895MHz, VCO 2709.47MHz, RD 1, FD 112.895 (m = 17, n = 19), OD 5, FOD 3, ERR -11.19ppm
// Measure: 100Hz-40kHz: 6.5ps
// 100Hz-1MHz: 67ps.
// 100Hz high pass: 215ps.
#define APP_PLL_CTL_45M  0x0A006F00
#define APP_PLL_DIV_45M  0x80000002
#define APP_PLL_FRAC_45M 0x80001012

// Found solution: IN 24.000MHz, OUT 24.576000MHz, VCO 2457.60MHz, RD 1, FD 102.400 (m = 2, n = 5), OD 5, FOD 5, ERR 0.0ppm
// Measure: 100Hz-40kHz: ~8ps
// 100Hz-1MHz: 63ps.
// 100Hz high pass: 127ps.
#define APP_PLL_CTL_24M  0x0A006500
#define APP_PLL_DIV_24M  0x80000004
#define APP_PLL_FRAC_24M 0x80000104

// Found solution: IN 24.000MHz, OUT 22.579186MHz, VCO 3522.35MHz, RD 1, FD 146.765 (m = 13, n = 17), OD 3, FOD 13, ERR -0.641ppm
// Measure: 100Hz-40kHz: 7ps
// 100Hz-1MHz: 67ps.
// 100Hz high pass: 260ps.
#define APP_PLL_CTL_22M  0x09009100
#define APP_PLL_DIV_22M  0x8000000C
#define APP_PLL_FRAC_22M 0x80000C10

#define APP_PLL_CTL_12M  0x0A006500
#define APP_PLL_DIV_12M  0x80000009
#define APP_PLL_FRAC_12M 0x80000104

#define APP_PLL_CTL_11M  0x09009100
#define APP_PLL_DIV_11M  0x80000009
#define APP_PLL_FRAC_11M 0x80000C10

#define APP_PLL_CTL_ENABLE (1 << 27)
#define APP_PLL_CLK_OUTPUT_ENABLE (1 << 16)

int AppPllEnable(int32_t clkFreq_hz)
{
    // Ensure the AppPLL is enabled
    unsigned data;
    read_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, data);
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, data | APP_PLL_CTL_ENABLE);

    // Turn off the clock output
    read_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, data);
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, data | APP_PLL_CLK_OUTPUT_ENABLE);

    unsigned ctrl;
    unsigned div;
    unsigned frac;

    switch(clkFreq_hz)
    {
        case 44100*256:
            ctrl = APP_PLL_CTL_11M;
            div = APP_PLL_DIV_11M;
            frac = APP_PLL_FRAC_11M;
            break;

         case 48000*256:
            ctrl = APP_PLL_CTL_12M;
            div = APP_PLL_DIV_12M;
            frac = APP_PLL_FRAC_12M;
            break;

        case 44100*512:
            ctrl = APP_PLL_CTL_22M;
            div = APP_PLL_DIV_22M;
            frac = APP_PLL_FRAC_22M;
            break;

        case 48000*512:
            ctrl = APP_PLL_CTL_24M;
            div = APP_PLL_DIV_24M;
            frac = APP_PLL_FRAC_24M;
            break;

        case 44100*1024:
            ctrl = APP_PLL_CTL_45M;
            div = APP_PLL_DIV_45M;
            frac = APP_PLL_FRAC_45M;
            break;

        case 48000*1024:
            ctrl = APP_PLL_CTL_49M;
            div = APP_PLL_DIV_49M;
            frac = APP_PLL_FRAC_49M;
            break;

        default:
            assert(0);
            break;
    }

    // Disable the PLL
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (ctrl & 0xF7FFFFFF));
    // Enable the PLL to invoke a reset on the appPLL.
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, ctrl);
    // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, ctrl);
    // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (ctrl & 0xF7FFFFFF));
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, ctrl);
    delay_microseconds(500);
    // Set the fractional divider if used
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM, frac);
    // Wait for PLL output frequency to stabilise due to fractional divider enable
    delay_microseconds(100);
    // Turn on the clock output
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, div);

	return 0;
}
