#include <xs1.h>
#include <assert.h>
#include <platform.h>
#include "xassert.h"
#include "i2c.h"
#include "xua.h"
#include "../../shared/apppll.h"

#include <print.h>

on tile[0]: port p_scl = XS1_PORT_1L;
on tile[0]: port p_sda = XS1_PORT_1M;
on tile[0]: out port p_ctrl = XS1_PORT_8D;

void ctrlPort()
{
    // Drive control port to turn on 3V3 and set MCLK_DIR
    // Note, "soft-start" to reduce current spike
    for (int i = 0; i < 30; i++)
    {
        p_ctrl <: 0xB0;
        delay_microseconds(5);
        p_ctrl <: 0xA0;
        delay_microseconds(5);
    }
}

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
#define PCM1865_GPIO01_FUN          (0x10) // Functionality control for GPIO0 and GPIO1.
#define PCM1865_GPIO01_DIR          (0x12) // Direction control for GPIO0 and GPIO1.
#define PCM1865_CLK_CFG0            (0x20) // Basic clock config.

unsafe client interface i2c_master_if i_i2c_client;

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

    AppPllEnable_SampleRate(DEFAULT_FREQ);
    
    // I2C mux takes the last byte written as the data for the control register.
    // We can't send only one byte so we send two with the data in the last byte.
    // We set "address" to 0 below as it's discarded by device.
    unsafe
    {
        result = i2c_reg_write(PCA9540B_I2C_DEVICE_ADDR, 0, PCA9540B_CTRL_CHAN_0);
    }

    if (result != I2C_REGOP_SUCCESS) 
    {
        printstr("I2C Mux I2C write reg failed\n");
    }

    // Setup ADCs
    // Setup is ADC is I2S slave, MCLK slave, I2S_DOUT2 on GPIO0. ADC sets up clocking automatically based on applied input clocks.
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_L,  0x42); // Set ADC2 Left input to come from VINL2[SE] input.
    WriteAllAdcRegs(PCM1865_ADC2_IP_SEL_R,  0x42); // Set ADC2 Right input to come from VINR2[SE] input.
    WriteAllAdcRegs(PCM1865_GPIO01_FUN,     0x05); // Set GPIO1 as normal polarity, GPIO1 functionality. Set GPIO0 as normal polarity, DOUT2 functionality.
    WriteAllAdcRegs(PCM1865_GPIO01_DIR,     0x04); // Set GPIO1 as an input. Set GPIO0 as an output (used for I2S DOUT2).
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_L,  0xFC); 
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH1_R,  0xFC); 
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_L,  0xFC); 
    WriteAllAdcRegs(PCM1865_PGA_VAL_CH2_R,  0xFC); 
    
    // Setup DACs
    // For basic I2S input we don't need any register setup. It does clock auto detect etc.
    // It holds DAC in reset until it gets clocks anyway.

}

/* Configures the external audio hardware for the required sample frequency */
void AudioHwConfig(unsigned samFreq, unsigned mClk, unsigned dsdMode, unsigned sampRes_DAC, unsigned sampRes_ADC)
{
    AppPllEnable_SampleRate(samFreq);
}
