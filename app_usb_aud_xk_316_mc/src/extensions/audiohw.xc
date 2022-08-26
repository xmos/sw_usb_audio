#include <xs1.h>
#include <assert.h>
#include <platform.h>
#include "xassert.h"
#include "i2c.h"
#include "xua.h"
#include "../../shared/apppll.h"

on tile[0]: port p_scl = XS1_PORT_1L;
on tile[0]: port p_sda = XS1_PORT_1M;
on tile[0]: out port p_ctrl = XS1_PORT_8D;

#if (XUA_SPDIF_RX_EN || ADAT_RX || (XUA_SYNCMODE == XUA_SYNCMODE_SYNC))
/* If we have an external digital input interface or running in synchronous mode we need to use the 
 * external CS2100 device for master clock generation */
#define USE_FRACTIONAL_N         (1)
#endif

/* p_ctrl:
 * [0:3] - Unused 
 * [4]   - EN_3v3_N
 * [5]   - EN_3v3A
 * [6]   - EXT_PLL_SEL (CS2100:0, SI: 1)
 * [7]   - MCLK_DIR    (Out:0, In: 1)
 */
#if defined(USE_FRACTIONAL_N)
#define EXT_PLL_SEL__MCLK_DIR    (0x00)
#else
#define EXT_PLL_SEL__MCLK_DIR    (0x80)
#endif
void ctrlPort()
{
    // Drive control port to turn on 3V3 and set MCLK_DIR
    // Note, "soft-start" to reduce current spike
    // Note, 3v3_EN is inverted
    for (int i = 0; i < 30; i++)
    {
        p_ctrl <: EXT_PLL_SEL__MCLK_DIR | 0x30; /* 3v3: off, 3v3A: on */
        delay_microseconds(5);
        p_ctrl <: EXT_PLL_SEL__MCLK_DIR | 0x20; /* 3v3: on, 3v3A: on */
        delay_microseconds(5);
    }
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

#if defined(USE_FRACTIONAL_N)
#define UNSAFE unsafe
#define CS2100_REGWRITE(reg, val)                   {result = i2c_reg_write(CS2100_I2C_DEVICE_ADDR, reg, val);}
#define CS2100_REGREAD_ASSERT(reg, data, expected)  {data[0] = i2c_reg_read(CS2100_I2C_DEVICE_ADDR, reg, result); assert(data[0] == expected);}
#define CS2100_I2C_DEVICE_ADDRESS                   (0x4E)
#include "../../shared/cs2100.h"
#undef UNSAFE
#endif

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

// PCM1865 (4-channel audio ADC) I2C Slave Addresses
#define PCM1865_0_I2C_DEVICE_ADDR   (0x4A)
#define PCM1865_1_I2C_DEVICE_ADDR   (0x4B)

// PCM1865 (4-channel audio ADC) Register Addresses
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

unsafe client interface i2c_master_if i_i2c_client;

void WriteAllAdcRegs(int reg_addr, int reg_data)
{
    i2c_regop_res_t result;

    unsafe
    {
        result = i2c_reg_write(PCM1865_0_I2C_DEVICE_ADDR, reg_addr, reg_data);
    }
    assert(result == I2C_REGOP_SUCCESS && msg("ADC0 I2C write reg failed"));

    unsafe
    {
        result = i2c_reg_write(PCM1865_1_I2C_DEVICE_ADDR, reg_addr, reg_data);
    }
    assert(result == I2C_REGOP_SUCCESS && msg("ADC1 I2C write reg failed"));
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
    size_t length;

    // Wait for power supply to come up.
    delay_milliseconds(100);

    /* Wait until global is set */
    unsafe
    {
        while(!(unsigned) i_i2c_client);
    }

#ifdef USE_FRACTIONAL_N
    /* Set external I2C mux to CS2100 */
    SetI2CMux(PCA9540B_CTRL_CHAN_1);

    unsafe
    {
        /* Use external CS2100 to generate master clock */
        PllInit(i_i2c_client);
    }
#else
    /* Use xCORE Secondary PLL to generate *fixed* master clock */
    AppPllEnable_SampleRate(DEFAULT_FREQ);
#endif
    /* Set external I2C mux to ADC's */
    SetI2CMux(PCA9540B_CTRL_CHAN_0);
    
    /*
     * Setup ADCs
     */
    /* Setup is ADC is I2S slave, MCLK slave, I2S_DOUT2 on GPIO0. ADC sets up clocking automatically based on applied input clocks.*/
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_L,  0x42); // Set ADC2 Left input to come from VINL2[SE] input.
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_R,  0x42); // Set ADC2 Right input to come from VINR2[SE] input.
    WriteAllAdcRegs(PCM1865_GPIO01_FUN,     0x05); // Set GPIO1 as normal polarity, GPIO1 functionality. Set GPIO0 as normal polarity, DOUT2 functionality.
    WriteAllAdcRegs(PCM1865_GPIO01_DIR,     0x04); // Set GPIO1 as an input. Set GPIO0 as an output (used for I2S DOUT2).
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_L,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_R,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_L,  0xFC);
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_R,  0xFC);

    if(XUA_PCM_FORMAT == XUA_PCM_FORMAT_TDM)
    {
        /* Write offset such that ADC's do not drive against eachother */
        result = i2c_reg_write(PCM1865_0_I2C_DEVICE_ADDR, PCM1865_TX_TDM_OFFSET, 1);
        assert(result == I2C_REGOP_SUCCESS && msg("ADC I2C write reg failed"));
        result = i2c_reg_write(PCM1865_1_I2C_DEVICE_ADDR, PCM1865_TX_TDM_OFFSET, 129);
        assert(result == I2C_REGOP_SUCCESS && msg("ADC I2C write reg failed"));
        
        /* RX_WLEN:        24-bit (default)
         * TDM_LRCLK_MODE: duty cycle of LRCLK is 1/256
         * TX_WLEN:        32-bit
         * FMT:            TDM/DSP
         */
        WriteAllAdcRegs(PCM1865_FMT, 0b01010011);
        
        /* TDM_OSEL:       4ch TDM 
         */
        WriteAllAdcRegs(PCM1865_TDM_OSEL, 0b00000001);
    }

    /*
     * Setup DACs
     */
    /* There are 4 DAC's on the board at I2C addresses 0x4C, 0x4D, 0x4E & 0x4F */
    if(XUA_PCM_FORMAT == XUA_PCM_FORMAT_TDM)
    {
        /* Note for TDM to work as expected for all DACs the jumpers marked "DAC I2S/TDM Config" need setting appropriately 
         * I2S MODE: SET ALL 2-3
         * TDM MODE: SET ALL 1-2, TDM SOURCE 3-4
         */
        for (int i = 0; i < 4; i++)
        { 
            /* Set Format to TDM/DSP & 24bit */
            result = i2c_reg_write(0x4C+i, 40, 0b00010011);
            assert(result == I2C_REGOP_SUCCESS && msg("DAC I2C write reg failed"));
        
            /* Set offset to appropriately for each DAC */
            result = i2c_reg_write(0x4C+i, 41, 1 + (i * 64));
            assert(result == I2C_REGOP_SUCCESS && msg("DAC I2C write reg failed"));
        }
    }
    else
    {
        // For basic I2S input we don't need any register setup. DACs will clock auto detect etc.
        // It holds DAC in reset until it gets clocks anyway.
    }

#ifdef USE_FRACTIONAL_N
    /* Set I2C mux back to CS2100 */
    SetI2CMux(PCA9540B_CTRL_CHAN_1);
#endif
}

/* Configures the external audio hardware for the required sample frequency */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)
{
#ifdef USE_FRACTIONAL_N
    PllMult(mClk, PLL_SYNC_FREQ, i_i2c_client);
#else
    AppPllEnable_SampleRate(samFreq);
#endif
}

