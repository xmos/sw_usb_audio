#include <xs1.h>
#include <assert.h>
#include <platform.h>
#include "xassert.h"
#include "i2c.h"
#include "xua.h"
#include "../../shared/apppll.h"

port p_scl = PORT_I2C_SCL;
port p_sda = PORT_I2C_SDA;
out port p_ctrl = PORT_CTRL;

// Other ports, (not used but defined here to stop 8 bit codec reset port driving them)
in port p_spi_miso  = PORT_SPI_MISO; // SPI MISO
in port p_spi_mosi  = PORT_SPI_MOSI; // SPI MOSI
in port p_spi_clk   = PORT_SPI_CLK;  // SPI CLK

/* p_ctrl:
 * [0:3] - Unused but overlaid with other signals
 * [4]   - CODEC_RST_N
 * [5]   - Unused
 * [6]   - Unused
 * [7]   - Unused
 */

void ctrlPort()
{
    // Get input from 3 ports in order to make them hi-z.
    p_spi_miso :> void;
    p_spi_mosi :> void;
    p_spi_clk  :> void;
    // Turn on the pulldowns on these ports to ensure they do not float.
    set_port_pull_down(p_spi_miso);
    set_port_pull_down(p_spi_mosi);
    set_port_pull_down(p_spi_clk);
    
    /* Reset CODEC. Just in case we've run another build config */
    // Note we must use CODEC_RST_N signal to reset CODEC registers. Reset bit only resets timing, not registers.
    p_ctrl <: 0x00; // Set CODEC_RST_N to 0 (default state, pulldown on board).
    delay_milliseconds(1);
    p_ctrl <: 0x10; // Set CODEC_RST_N to 1
    delay_milliseconds(100); // Wait 100ms for CODEC internal LDO to power up and be ready and ADC init cycle to run.
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

#define UNSAFE unsafe
#undef UNSAFE

// AK4558 (stereo audio CODEC) I2C Slave Address
#define AK4558_I2C_DEVICE_ADDR    0x10

// AK4558 (stereo audio CODEC) I2C Register Addresses
#define AK4558_PWR_MNGMT      0x00 // Power Management
#define AK4558_PLL_CTRL       0x01 // PLL Control
#define AK4558_DAC_TDM        0x02 // DAC TDM
#define AK4558_CTRL1          0x03 // Control 1
#define AK4558_CTRL2          0x04 // Control 2
#define AK4558_MODE_CTRL      0x05 // Mode Control
#define AK4558_FILTER_SET     0x06 // Filter Setting
#define AK4558_HPF_EN_FILT    0x07 // HPF Enable, Filter setting
#define AK4558_VOL_L          0x08 // LOUT Volume Control
#define AK4558_VOL_R          0x09 // ROUT Volume Control

unsafe client interface i2c_master_if i_i2c_client;

void write_codec_reg(int regAddr, int regData)
{
  i2c_regop_res_t result;
  
  unsafe
  {
      result = i2c_reg_write(AK4558_I2C_DEVICE_ADDR, regAddr, regData);
  }
  assert(result == I2C_REGOP_SUCCESS && msg("CODEC I2C write reg failed"));
}

/* Configures the external audio hardware at startup */
void AudioHwInit()
{
    i2c_regop_res_t result;

    // Wait for power supply to come up.
    // delay_milliseconds(100);

    /* Wait until global is set */
    unsafe
    {
        while(!(unsigned) i_i2c_client);
    }

    /* Use xCORE Secondary PLL to generate *fixed* master clock */
    if (DEFAULT_FREQ % 22050 == 0)
    {
        AppPllEnable(MCLK_441);
    }
    else
    {
        AppPllEnable(MCLK_48);
    }

    /*
     * Setup CODEC
     */
    if(CODEC_MASTER)
    {
        // ToDo: Add register config for when the CODEC is I2S master.
    }
    else
    {
        write_codec_reg(AK4558_CTRL1,     0x39); // Set 32 bit I2S mode for DIF, set DAC Soft Mute active.
        write_codec_reg(AK4558_CTRL2,     0x01); // Set auto clock mode bit and other bits become irrelevant.
        write_codec_reg(AK4558_VOL_L,     0xFF); // Set Left channel volume to 0dB.
        write_codec_reg(AK4558_VOL_R,     0xFF); // Set Right channel volume to 0dB.
        write_codec_reg(AK4558_MODE_CTRL, 0x2B); // Set the DAC in power save mode. LOPS bit 0 -> 1.
        write_codec_reg(AK4558_PWR_MNGMT, 0x1F); // Power up DAC and ADC: PMDAL, PMDAR, PMADL, PMADR 0 -> 1.
        delay_milliseconds(1000);                // Wait a long time for DAC common mode output voltage to stabilise.
        write_codec_reg(AK4558_MODE_CTRL, 0x2A); // Release the DAC from power save mode. LOPS bit 1 -> 0.
    }

}

/* Configures the external audio hardware for the required sample frequency */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    // Soft mute the DAC to try to avoid pop noise. Is this pointless as we won't be outputting data anyway when we get to this point?
    write_codec_reg(AK4558_CTRL1, 0x39); // Set 32 bit I2S mode for DIF, set DAC Soft Mute active.
    delay_milliseconds(100);

    if (samFreq % 22050 == 0)
    {
        AppPllEnable(MCLK_441);
    }
    else
    {
        AppPllEnable(MCLK_48);
    }

    // Release DAC from soft mute to try to avoid pop noise. Is this pointless as we won't be outputting data anyway when we get to this point?
    write_codec_reg(AK4558_CTRL1, 0x38); // Set 32 bit I2S mode for DIF, set DAC Soft Mute inactive.
    delay_milliseconds(100);

}

