#include <xs1.h>
#include <assert.h>
#include <platform.h>
#include "xassert.h"
#include "i2c.h"
#include "xua.h"

extern "C" {
    #include "sw_pll.h"
}

#if (XUA_PCM_FORMAT == XUA_PCM_FORMAT_TDM) && (XUA_I2S_N_BITS != 32)
#warning ADC only supports TDM operation at 32 bits
#endif

#ifndef I2S_LOOPBACK
#define I2S_LOOPBACK             (0)
#endif

port p_scl = PORT_I2C_SCL;
port p_sda = PORT_I2C_SDA;
out port p_ctrl = PORT_CTRL;                /* p_ctrl:
                                             * [0:3] - Unused
                                             * [4]   - EN_3v3_N    (1v0 hardware only)
                                             * [5]   - EN_3v3A
                                             * [6]   - EXT_PLL_SEL (CS2100:0, SI: 1)
                                             * [7]   - MCLK_DIR    (Out:0, In: 1)
                                             */

on tile[0]: in port p_margin = XS1_PORT_1G;  /* CORE_POWER_MARGIN:   Driven 0:   0.925v
                                              *                      Pull down:  0.922v
                                              *                      High-z:     0.9v
                                              *                      Pull-up:    0.854v
                                              *                      Driven 1:   0.85v
                                              */

#if ((XUA_SYNCMODE == XUA_SYNCMODE_SYNC || XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN) && !XUA_USE_SW_PLL)
/* Recover external clock using sw_pll by default when using digital Rx or sync mode.
   Use CS2100 if XUA_USE_SW_PLL is set to 0. All other configs used a fixed clock
   generared by sw_pll */
#define USE_FRACTIONAL_N         (1)
#else
#define USE_FRACTIONAL_N         (0)
#endif

#if (USE_FRACTIONAL_N)
#define EXT_PLL_SEL__MCLK_DIR    (0x00)
#else
#define EXT_PLL_SEL__MCLK_DIR    (0x80)
#endif

/* Board setup for XU316 MC Audio (1v1) */
void board_setup()
{
    /* "Drive high mode" - drive high for 1, non-driving for 0 */
    set_port_drive_high(p_ctrl);

    /* Ensure high-z for 0.9v */
    p_margin :> void;

    /* Drive control port to turn on 3V3 and mclk direction appropriately.
     * Bits set to low will be high-z, pulled down */
    p_ctrl <: EXT_PLL_SEL__MCLK_DIR | 0x20;

    /* Wait for power supplies to be up and stable */
    delay_milliseconds(10);
}

/* Working around not being able to extend an unsafe interface (Bugzilla #18670)*/
i2c_regop_res_t i2c_reg_write(uint8_t device_addr, uint8_t reg, uint8_t data)
{
    uint8_t a_data[2] = {reg, data};
    size_t n;

    unsafe
    {
        i_i2c_client.write(device_addr, a_data, 2, n, 1);
    }

    if (n == 0)
    {
        return I2C_REGOP_DEVICE_NACK;
    }
    if (n < 2)
    {
        return I2C_REGOP_INCOMPLETE;
    }

    return I2C_REGOP_SUCCESS;
}

uint8_t i2c_reg_read(uint8_t device_addr, uint8_t reg, i2c_regop_res_t &result)
{
    uint8_t a_reg[1] = {reg};
    uint8_t data[1] = {0};
    size_t n;
    i2c_res_t res;

    unsafe
    {
        res = i_i2c_client.write(device_addr, a_reg, 1, n, 0);

        if (n != 1)
        {
            result = I2C_REGOP_DEVICE_NACK;
            i_i2c_client.send_stop_bit();
            return 0;
        }

        res = i_i2c_client.read(device_addr, data, 1, 1);
    }

    if (res == I2C_ACK)
    {
        result = I2C_REGOP_SUCCESS;
    }
    else
    {
        result = I2C_REGOP_DEVICE_NACK;
    }
    return data[0];
}

/* The number of timer ticks to wait for the audio PLL to lock */
/* CS2100 lists typical lock time as 100 * input period */
#define AUDIO_PLL_LOCK_DELAY        (40000000)

#define CS2100_REGWRITE(reg, val)                   {result = i2c_reg_write(CS2100_I2C_DEVICE_ADDR, reg, val);}
#define CS2100_REGREAD_ASSERT(reg, data, expected)  {data[0] = i2c_reg_read(CS2100_I2C_DEVICE_ADDR, reg, result); assert(data[0] == expected);}
#define CS2100_I2C_DEVICE_ADDRESS                   (0x4E)
#define UNSAFE unsafe
#include "../../shared/cs2100.h"
#undef UNSAFE

// PCA9540B (2-channel I2C-bus mux) I2C Slave Address
#define PCA9540B_I2C_DEVICE_ADDR    (0x70)

// PCA9540B (2-channel I2C-bus mux) Control Register Values
#define PCA9540B_CTRL_CHAN_0        (0x04) // Set Control Register to select channel 0
#define PCA9540B_CTRL_CHAN_1        (0x05) // Set Control Register to select channel 1
#define PCA9540B_CTRL_CHAN_NONE     (0x00) // Set Control Register to select neither channel

// PCM5122 (2-channel audio DAC) I2C Slave Addresses
#define PCM5122_0_I2C_DEVICE_ADDR   (0x4C)
#define PCM5122_1_I2C_DEVICE_ADDR   (0x4D)
#define PCM5122_2_I2C_DEVICE_ADDR   (0x4E)
#define PCM5122_3_I2C_DEVICE_ADDR   (0x4F)

// PCM5122 (2-channel audio DAC) Register Addresses
#define PCM5122_PAGE              0x00 // Page select
#define PCM5122_RESET             0x01 // Reset control
#define PCM5122_STANDBY_PWDN      0x02 // Standby/Power Down control
#define PCM5122_MUTE              0x03 // Mute control
#define PCM5122_PLL               0x04 // PLL control
#define PMC5122_DE_SDOUT          0x07 // De-Emphasis and SDOUT Select
#define PMC5122_GPIO_ENABLE       0x08 // GPIO enables
#define PCM5122_BCK_LRCLK         0x09 // BCK, LRCLK configuration
#define PCM5122_RBCK_LRCLK        0x0C // BCK, LRCLK reset
#define PCM5122_SDAC              0x0E // DAC Clock Source Select
#define PCM5122_PLL_P             0x14 // PLL P divider
#define PCM5122_PLL_J             0x15 // PLL J divider
#define PCM5122_PLL_D1            0x16 // PLL D1 divider
#define PCM5122_PLL_D2            0x17 // PLL D2 divider
#define PCM5122_PLL_R             0x18 // PLL R divider
#define PCM5122_DDSP              0x1B // DSP clock divider
#define PCM5122_DDAC              0x1C // DAC clock divider
#define PCM5122_DNCP              0x1D // Negative Charge Pump clock divider
#define PCM5122_DOSR              0x1E // Oversampling Ratio divider
#define PCM5122_DBCK              0x20 // Master mode BCK divider
#define PCM5122_DLRCK             0x21 // Master mode LRCK divider
#define PCM5122_I16E_FS           0x22 // 16x Interpolate/FS Speed Mode.
#define PCM5122_IDAC_MS           0x23 // IDAC[15:8]
#define PCM5122_IDAC_LS           0x24 // IDAC[7:0]
#define PCM5122_CLK_DET           0x25 // Clock detection/control
#define PCM5122_I2S               0x28 // I2S configuration
#define PCM5122_I2S_SHIFT         0x29 // I2S shift
#define PCM5122_AUTO_MUTE         0x41 // Auto Mute
#define PCM5122_GPIO_OUT_SEL      0x55 // GPIOn output selection

// PCM1865 (4-channel audio ADC) I2C Slave Addresses
#define PCM1865_0_I2C_DEVICE_ADDR   (0x4A)
#define PCM1865_1_I2C_DEVICE_ADDR   (0x4B)

// PCM1865 (4-channel audio ADC) Register Addresses
#define PCM1865_RESET               (0x00)
#define PCM1865_PGA_VAL_CH1_L       (0x01)
#define PCM1865_PGA_VAL_CH1_R       (0x02)
#define PCM1865_PGA_VAL_CH2_L       (0x03)
#define PCM1865_PGA_VAL_CH2_R       (0x04)
#define PCM1865_ADC2_IP_SEL_L       (0x08) // Select input to route to ADC2 left input.
#define PCM1865_ADC2_IP_SEL_R       (0x09) // Select input to route to ADC2 right input.
#define PCM1865_FMT                 (0x0B) // RX_WLEN, TDM_LRCLK_MODE, TX_WLEN, FMT
#define PCM1865_TDM_OSEL            (0x0C)
#define PCM1865_TX_TDM_OFFSET       (0x0D)
#define PCM1865_GPIO01_FUN          (0x10) // Functionality control for GPIO0 and GPIO1.
#define PCM1865_GPIO01_DIR          (0x12) // Direction control for GPIO0 and GPIO1.
#define PCM1865_CLK_CFG0            (0x20) // Basic clock config.
#define PCM1865_PWR_STATE           (0x70) // Power down, Sleep, Standby

unsafe client interface i2c_master_if i_i2c_client;

void WriteRegs(int deviceAddr, int numDevices, int regAddr, int regData)
{
    i2c_regop_res_t result;

    for(int i = deviceAddr; i < (deviceAddr + numDevices); i++)
    {
        unsafe
        {
            result = i2c_reg_write(i, regAddr, regData);
        }
        assert(result == I2C_REGOP_SUCCESS && msg("I2C write reg failed"));
    }
}

/* Note, this function assumes contiguous devices addresses */
void WriteAllDacRegs(int regAddr, int regData)
{
    WriteRegs(PCM5122_0_I2C_DEVICE_ADDR, 4, regAddr, regData);
}

/* Note, this function assumes contiguous devices addresses */
void WriteAllAdcRegs(int regAddr, int regData)
{
    WriteRegs(PCM1865_0_I2C_DEVICE_ADDR, 2, regAddr, regData);
}

void SetI2CMux(int ch)
{
    i2c_regop_res_t result;

    // I2C mux takes the last byte written as the data for the control register.
    // We can't send only one byte so we send two with the data in the last byte.
    // We set "address" to 0 below as it's discarded by device.
    unsafe
    {
        result = i2c_reg_write(PCA9540B_I2C_DEVICE_ADDR, 0, ch);
    }

    assert(result == I2C_REGOP_SUCCESS && msg("I2C Mux I2C write reg failed"));
}

/* Configures the external audio hardware at startup */
void AudioHwInit()
{
    i2c_regop_res_t result;

    // Wait for power supply to come up.
    delay_milliseconds(100);

    /* Wait until global is set */
    unsafe
    {
        while(!(unsigned) i_i2c_client);
    }

    if(USE_FRACTIONAL_N)
    {
        /* Set external I2C mux to CS2100 */
        SetI2CMux(PCA9540B_CTRL_CHAN_1);

        unsafe
        {
            /* Use external CS2100 to generate master clock */
            PllInit(i_i2c_client);
        }
    }
    else if((XUA_SYNCMODE == XUA_SYNCMODE_SYNC || XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN) && XUA_USE_SW_PLL)
    {
        /* Do nothing - the SW_PLL configures the AppPLL */
    }
    else
    {
        /* Use xCORE Secondary PLL to generate *fixed* master clock */
        if (DEFAULT_FREQ % 22050 == 0)
        {
            sw_pll_fixed_clock(MCLK_441);
        }
        else
        {
            sw_pll_fixed_clock(MCLK_48);
        }
    }

    /* Set external I2C mux to DACs/ADCs */
    SetI2CMux(PCA9540B_CTRL_CHAN_0);

    /* Reset DAC & ADC registers. Just in case we've run another build config */
    WriteAllDacRegs(PCM5122_PAGE,           0x00); // Set Page 0.
    WriteAllDacRegs(PCM5122_STANDBY_PWDN,   0x10); // Request standby mode
    delay_milliseconds(1);
    WriteAllDacRegs(PCM5122_RESET,          0x11); // Reset dac modules and registers to defaults. but this sets standby to 0 so chip starts up ... need to put back in standby.
    WriteAllDacRegs(PCM5122_STANDBY_PWDN,   0x10); // Request standby mode
    WriteAllAdcRegs(PCM1865_RESET, 0xFE);

    /*
     * Setup ADCs
     */
    /* Setup is ADC is I2S slave, MCLK slave, I2S_DOUT2 on GPIO0. ADC sets up clocking automatically based on applied input clocks */
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_L,  0x42); // Set ADC2 Left input to come from VINL2[SE] input.
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_R,  0x42); // Set ADC2 Right input to come from VINR2[SE] input.
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_L,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_R,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_L,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_R,  0xFC);

    if (XUA_PCM_FORMAT == XUA_PCM_FORMAT_I2S)
    {
        /* Convert XUA_I2S_N_BITS to ADC FMT bits */
        int tx_wlen = 0;
        switch(XUA_I2S_N_BITS)
        {
            case 32:
                tx_wlen = 0b00;
                break;
            case 24:
                tx_wlen = 0b01;
                break;
            case 16:
                tx_wlen = 0b11;
                break;
        }

        /* Only enable DOUT2 in I2S mode. In TDM mode it doesn't really make sense, wastes power (and data sheet states "not available") */
        WriteAllAdcRegs(PCM1865_GPIO01_FUN,     0x05); // Set GPIO1 as normal polarity, GPIO1 functionality. Set GPIO0 as normal polarity, DOUT2 functionality.
        WriteAllAdcRegs(PCM1865_GPIO01_DIR,     0x04); // Set GPIO1 as an input. Set GPIO0 as an output (used for I2S DOUT2).

        /* RX_WLEN:        24-bit (default)
         * TDM_LRCLK_MODE: 0 (default)
         * TX_WLEN:        XUA_I2S_N_BITS
         * FMT:            I2S
         */
        WriteAllAdcRegs(PCM1865_FMT, 0b01000000 | (tx_wlen << 2));
    }
    else
    {
        /* Note, the ADCs do not support TDM with channel slots other than 32bit i.e. 256fs */
        /* Write offset such that ADC's do not drive against eachother */
        result = i2c_reg_write(PCM1865_0_I2C_DEVICE_ADDR, PCM1865_TX_TDM_OFFSET, 1);
        assert(result == I2C_REGOP_SUCCESS && msg("ADC I2C write reg failed"));
        result = i2c_reg_write(PCM1865_1_I2C_DEVICE_ADDR, PCM1865_TX_TDM_OFFSET, 129);
        assert(result == I2C_REGOP_SUCCESS && msg("ADC I2C write reg failed"));

        if(CODEC_MASTER)
        {
            /* PCM5122 drives a 1/2 duty cycle LRCLK for TDM */
            /* RX_WLEN:        24-bit (default)
             * TDM_LRCLK_MODE: duty cycle of LRCLK is 1/2
             * TX_WLEN:        32-bit
             * FMT:            TDM/DSP
             */
            WriteAllAdcRegs(PCM1865_FMT, 0b01000011);
        }
        else
        {
            /* xCORE drives 1/256 duty cycle LRCLK for TDM */
            /* RX_WLEN:        24-bit (default)
             * TDM_LRCLK_MODE: duty cycle of LRCLK is 1/256
             * TX_WLEN:        32-bit
             * FMT:            TDM/DSP
             */
            WriteAllAdcRegs(PCM1865_FMT, 0b01010011);
        }

        /* TDM_OSEL:       4ch TDM
         */
        WriteAllAdcRegs(PCM1865_TDM_OSEL, 0b00000001);
    }

    /*
     * Setup DACs
     */
    if(CODEC_MASTER)
    {
        /* When xCORE is I2S slave we set one DAC to master and the rest remain slaves.
         * We write some values to all DACs just to avoid any difference in performance */

        // Disable Auto Clock Configuration
        WriteAllDacRegs(PCM5122_CLK_DET, 0x72);

        // PLL P divider to 2
        WriteAllDacRegs(PCM5122_PLL_P, 0x01);

        // PLL J divider to 8
        WriteAllDacRegs(PCM5122_PLL_J, 0x08);

        // PLL D1 divider to 00
        WriteAllDacRegs(PCM5122_PLL_D1, 0x00);

        // PLL D2 divider to 00
        WriteAllDacRegs(PCM5122_PLL_D2, 0x00);

        // PLL R divider to 1
        WriteAllDacRegs(PCM5122_PLL_R, 0x00);

        // NB: Overall PLL Multiplier is x4.
        // miniDSP CLK divider (NMAC) to 2
        WriteAllDacRegs(PCM5122_DDSP, 0x01);

        //DAC CLK divider to 16
        WriteAllDacRegs(PCM5122_DDAC, 0x0F);

        // NCP CLK divider to 4
        WriteAllDacRegs(PCM5122_DNCP, 0x03);

        // IDAC2
        WriteAllDacRegs(PCM5122_IDAC_LS, 0x00);
    }
    else
    {
        WriteAllDacRegs(PCM5122_CLK_DET,        0x02); // disable clock autoset.
        WriteAllDacRegs(PCM5122_PLL,            0x00); // disable the internal PLL.
        WriteAllDacRegs(PCM5122_AUTO_MUTE,      0x00); // disable auto mute.
        WriteAllDacRegs(PCM5122_DDSP,           0x00); // sets DSP clock divider NMAC to 1.
        WriteAllDacRegs(PCM5122_DNCP,           0x03); // sets charge pump divider NCP to 4. (same for all modes, this governs charge pump frequency (divided from *DAC* clock)).
    }

    int alen = 0b11;
    switch(XUA_I2S_N_BITS)
    {
        case 16:
            alen = 0b00;
            break;
        case 24:
            alen = 0b10;
            break;
        case 32:
            alen = 0b11;
            break;
    }

    if(XUA_PCM_FORMAT == XUA_PCM_FORMAT_I2S)
    {
        /* Set Format to I2S with word length XUA_I2S_N_BITS */
        WriteAllDacRegs(PCM5122_I2S, 0b00000000 | (alen));
    }
    else
    {
        /* Note, for TDM to work as expected for all DACs the jumpers on the board marked "DAC I2S/TDM Config" need setting appropriately
         * I2S MODE: SET ALL 2-3
         * TDM MODE: SET ALL 1-2, TDM SOURCE 3-4
         */
        /* Set Format to TDM/DSP with word length XUA_I2S_N_BITS */
        WriteAllDacRegs(PCM5122_I2S, 0b00010000 | (alen));

        /* Set offset to appropriately for each DAC */
        for(int dacAddr = PCM5122_0_I2C_DEVICE_ADDR; dacAddr < (PCM5122_0_I2C_DEVICE_ADDR+4); dacAddr++)
        {
            const int dacOffset = dacAddr - PCM5122_0_I2C_DEVICE_ADDR;
            result = i2c_reg_write(dacAddr, PCM5122_I2S_SHIFT, 1 + (dacOffset * XUA_I2S_N_BITS * 2));
            assert(result == I2C_REGOP_SUCCESS && msg("DAC I2C write reg failed"));
        }
    }

    if(I2S_LOOPBACK)
    {
        WriteAllAdcRegs(PCM1865_RESET, 0xFE);           // Reset all ADC registers.
        WriteAllAdcRegs(PCM1865_PWR_STATE, 0x77);       // Sets ADCs into powerdown.
        WriteAllAdcRegs(PCM1865_FMT, 0b01010011);       // Sets 1/256 TDM mode, 32bit TX_WLEN
        WriteAllAdcRegs(PCM1865_TX_TDM_OFFSET, 191);    // Sets TX_TDM_OFFSET to 191
                                                        // Note, expect ADCs to clash with DAC channels 7/8 in loopback TDM mode

        WriteAllDacRegs(PMC5122_DE_SDOUT, 0x01);
        WriteAllDacRegs(PCM5122_GPIO_OUT_SEL, 0x07);
        WriteAllDacRegs(PMC5122_GPIO_ENABLE, 0x20);
    }
}

/* Configures the external audio hardware for the required sample frequency */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    WriteAllDacRegs(PCM5122_MUTE,           0x11); // Soft Mute both channels
    delay_milliseconds(3);  // Wait for mute to take effect. This takes 104 samples, this is 2.4ms @ 44.1kHz. So lets say 3ms to cover everything.
    WriteAllDacRegs(PCM5122_STANDBY_PWDN,   0x10); // Request standby mode while we change regs

    if (USE_FRACTIONAL_N)
    {
        timer t;
        unsigned time;

        SetI2CMux(PCA9540B_CTRL_CHAN_1);
        PllMult(mClk, PLL_SYNC_FREQ, i_i2c_client);

        /* Allow some time for mclk to lock and MCLK to stabilise - this is important to avoid glitches at start of stream */
        t :> time;
        t when timerafter(time+AUDIO_PLL_LOCK_DELAY) :> void;

        SetI2CMux(PCA9540B_CTRL_CHAN_0);
    }
    else if((XUA_SYNCMODE == XUA_SYNCMODE_SYNC || XUA_SPDIF_RX_EN || XUA_ADAT_RX_EN) && XUA_USE_SW_PLL)
    {
        /* Do nothing - the SW_PLL configures the AppPLL */
    }
    else
    {
        sw_pll_fixed_clock(mClk);
    }

    /* Set one DAC to I2S master */
    if(CODEC_MASTER)
    {
        i2c_regop_res_t result = I2C_REGOP_SUCCESS;
        unsigned regVal;
        const int dacAddr = PCM5122_3_I2C_DEVICE_ADDR;

        //OSR CLK divider is set to one (as its based on the output from the DAC CLK, which is already PLL/16)
        regVal = (mClk/(samFreq * I2S_CHANS_PER_FRAME * 32))-1;
        result |= i2c_reg_write(dacAddr, PCM5122_DOSR, regVal);

        //# FS setting should be set based on sample rate
        regVal = samFreq/96000;
        result |= i2c_reg_write(dacAddr, PCM5122_I16E_FS, regVal);

        //IDAC1  sets the number of miniDSP instructions per clock.
        regVal = 192000/samFreq;
        result |= i2c_reg_write(dacAddr, PCM5122_IDAC_MS, regVal);

        /* Master mode setting */
        // BCK, LRCK output
        result |= i2c_reg_write(dacAddr, PCM5122_BCK_LRCLK, 0x11);

        // Master mode BCK divider setting (making 64fs)
        regVal = (mClk/(samFreq * I2S_CHANS_PER_FRAME * XUA_I2S_N_BITS))-1;
        result |= i2c_reg_write(dacAddr, PCM5122_DBCK, regVal);

        // Master mode LRCK divider setting (divide BCK by a further 64 (256 for TDM) to make 1fs)
        regVal = (I2S_CHANS_PER_FRAME * XUA_I2S_N_BITS)-1;
        result |= i2c_reg_write(dacAddr, PCM5122_DLRCK, regVal);

        // Master mode BCK, LRCK divider reset release
        result |= i2c_reg_write(dacAddr, PCM5122_RBCK_LRCLK, 0x3f);

        assert(result == I2C_REGOP_SUCCESS && msg("DAC I2C write reg failed"));
    }
    else
    {
        // Do any changes to input clocks here
        // The following divider generates the DAC clock from the master clock.
        // DAC clock needs to be 5.6448MHz for 44.1/88.2/176.4kHz SRs and 6.144MHz for 48/96/192 SRs.
        // So if using 22.5792/24.576 MCLK this needs to be 4. For 45.1584/49.152MHz this needs to be 8. Note to set a divider of 4 we write 0x03.
        WriteAllDacRegs(PCM5122_DDAC,           0x03); // sets DAC clock divider NDAC to 4.

        // IDAC is how many DSP clocks are present in an audio frame.
        // DSP clock in this system is equal to Master clock (as NMAC = 1 set above).
        // So IDAC becomes the ratio of Fs to MCLK.
        // For 22.5792/24.576MHz MCLK this is 512 for 44.1/48, 256 for 88.2/96, 128 for 176.4/192 and 64 for 352.8/384.
        // For 45.1584/49.152MHz MCLK this is 1024 for 44.1/48, 512 for 88.2/96, 256 for 176.4/192 and 128 for 352.8/384.
        // Settings below are for 22.5792/24.576.

        if(samFreq <= 48000)
        {
            WriteAllDacRegs(PCM5122_DOSR,         0x07); // Set OSR divider to 8.
            WriteAllDacRegs(PCM5122_I16E_FS,      0x00); // Set FS to single speed mode
            WriteAllDacRegs(PCM5122_IDAC_MS,      0x02); // IDAC MS Byte
            WriteAllDacRegs(PCM5122_IDAC_LS,      0x00); // IDAC LS Byte
        }
        else if((samFreq > 48000) && (samFreq <= 96000))
        {
            WriteAllDacRegs(PCM5122_DOSR,         0x03); // Set OSR divider to 4.
            WriteAllDacRegs(PCM5122_I16E_FS,      0x01); // Set FS to double speed mode
            WriteAllDacRegs(PCM5122_IDAC_MS,      0x01); // IDAC MS Byte
            WriteAllDacRegs(PCM5122_IDAC_LS,      0x00); // IDAC LS Byte
        }
        else if((samFreq > 96000) && (samFreq <= 192000))
        {
            WriteAllDacRegs(PCM5122_DOSR,         0x01); // Set OSR divider to 2.
            WriteAllDacRegs(PCM5122_I16E_FS,      0x02); // Set FS to quad speed mode
            WriteAllDacRegs(PCM5122_IDAC_MS,      0x00); // IDAC MS Byte
            WriteAllDacRegs(PCM5122_IDAC_LS,      0x80); // IDAC LS Byte
        }
        else if((samFreq > 192000) && (samFreq <= 384000)) // In case we ever use this mode.
        {
            WriteAllDacRegs(PCM5122_DOSR,         0x00); // Set OSR divider to 1.
            WriteAllDacRegs(PCM5122_I16E_FS,      0x03); // Set FS to octal speed mode
            WriteAllDacRegs(PCM5122_IDAC_MS,      0x00); // IDAC MS Byte
            WriteAllDacRegs(PCM5122_IDAC_LS,      0x40); // IDAC LS Byte
        }
    }

    WriteAllDacRegs(PCM5122_STANDBY_PWDN,   0x00); // Set DAC in run mode (no standby or powerdown)
    delay_milliseconds(1);
    WriteAllDacRegs(PCM5122_MUTE,           0x00); // Un-mute both channels
}

