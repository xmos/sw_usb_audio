#include <platform.h>
#include <stdint.h>

// App PLL setup
#define APP_PLL_CTL_BYPASS       (0)   // 0 = no bypass, 1 = bypass.
#define APP_PLL_CTL_INPUT_SEL    (0)   // 0 = XTAL, 1 = sysPLL
#define APP_PLL_CTL_ENABLE       (1)   // 0 = disabled, 1 = enabled.

// 24MHz in, 24.576MHz out, integer mode
// Found exact solution:   IN  24000000.0, OUT  24576000.0, VCO 2457600000.0, RD  5, FD  512, OD 10, FOD  10
#define APP_PLL_CTL_OD_48        (4)   // Output divider = (OD+1)
#define APP_PLL_CTL_F_48         (511) // FB divider = (F+1)/2
#define APP_PLL_CTL_R_48         (4)   // Ref divider = (R+1)

#define APP_PLL_CTL_48           ((APP_PLL_CTL_BYPASS << 29) | (APP_PLL_CTL_INPUT_SEL << 28) | (APP_PLL_CTL_ENABLE << 27) |\
                                    (APP_PLL_CTL_OD_48 << 23) | (APP_PLL_CTL_F_48 << 8) | APP_PLL_CTL_R_48)

// Fractional divide is M/N
#define APP_PLL_FRAC_EN_48             (0)   // 0 = disabled
#define APP_PLL_FRAC_NPLUS1_CYCLES_48  (0)   // M value is this reg value + 1.
#define APP_PLL_FRAC_TOTAL_CYCLES_48   (0)   // N value is this reg value + 1.
#define APP_PLL_FRAC_48          ((APP_PLL_FRAC_EN_48 << 31) | (APP_PLL_FRAC_NPLUS1_CYCLES_48 << 8) | APP_PLL_FRAC_TOTAL_CYCLES_48)

// 24MHz in, 22.5792MHz out (44.1kHz * 512), frac mode
// Found exact solution:   IN  24000000.0, OUT  22579200.0, VCO 2257920000.0, RD  5, FD  470.400 (m =   2, n =   5), OD  5, FOD   10
#define APP_PLL_CTL_OD_441       (4)   // Output divider = (OD+1)
#define APP_PLL_CTL_F_441        (469) // FB divider = (F+1)/2
#define APP_PLL_CTL_R_441        (4)   // Ref divider = (R+1)

#define APP_PLL_CTL_441          ((APP_PLL_CTL_BYPASS << 29) | (APP_PLL_CTL_INPUT_SEL << 28) | (APP_PLL_CTL_ENABLE << 27) |\
                                    (APP_PLL_CTL_OD_441 << 23) | (APP_PLL_CTL_F_441 << 8) | APP_PLL_CTL_R_441)

#define APP_PLL_FRAC_EN_44             (1)   // 1 = enabled
#define APP_PLL_FRAC_NPLUS1_CYCLES_44  (1)   // M value is this reg value + 1.
#define APP_PLL_FRAC_TOTAL_CYCLES_44   (4)   // N value is this reg value + 1.define APP_PLL_CTL_R_441        (4)   // Ref divider = (R+1)
#define APP_PLL_FRAC_44   ((APP_PLL_FRAC_EN_44 << 31) | (APP_PLL_FRAC_NPLUS1_CYCLES_44 << 8) | APP_PLL_FRAC_TOTAL_CYCLES_44)

#define APP_PLL_DIV_INPUT_SEL    (1)   // 0 = sysPLL, 1 = app_PLL
#define APP_PLL_DIV_DISABLE      (0)   // 1 = disabled (pin connected to X1D11), 0 = enabled divider output to pin.
#define APP_PLL_DIV_VALUE        (4)   // Divide by N+1 - remember there's a /2 also afterwards for 50/50 duty cycle.
#define APP_PLL_DIV              ((APP_PLL_DIV_INPUT_SEL << 31) | (APP_PLL_DIV_DISABLE << 16) | APP_PLL_DIV_VALUE)

/* TODO support more than two freqs..*/
int AppPllEnable(int32_t clkFreq_hz)
{
    switch(clkFreq_hz)
    {
        case 44100*512:

            // Disable the PLL
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
            // Enable the PLL to invoke a reset on the appPLL.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
            // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);
            // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_441 & 0xF7FFFFFF));
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_441);

            // Set the fractional divider if used
            write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM, APP_PLL_FRAC_44);

            break;

        case 48000*512:

            // Disable the PLL
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_48 & 0xF7FFFFFF));
            // Enable the PLL to invoke a reset on the appPLL.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);
            // Must write the CTL register twice so that the F and R divider values are captured using a running clock.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);
            // Now disable and re-enable the PLL so we get the full 5us reset time with the correct F and R values.
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, (APP_PLL_CTL_48 & 0xF7FFFFFF));
            write_node_config_reg(tile[1], XS1_SSWITCH_SS_APP_PLL_CTL_NUM, APP_PLL_CTL_48);

            // Set the fractional divider if used
            write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_PLL_FRAC_N_DIVIDER_NUM, APP_PLL_FRAC_48);

            break;

        default:
            assert(0);
            break;
    }

    // Wait for PLL output frequency to stabilise due to fractional divider enable
    delay_microseconds(100);

    // Turn on the clock output
    write_node_config_reg(tile[0], XS1_SSWITCH_SS_APP_CLK_DIVIDER_NUM, APP_PLL_DIV);

	return 0;
}

int AppPllEnable_SampleRate(int32_t sampleRate_hz)
{
    assert(sampleRate_hz >= 22050);

    if(sampleRate_hz % 22050 == 0)
    {
        AppPllEnable(44100*512);
    }
    else
    {
        AppPllEnable(48000*512);
    }

	return 0;
}

