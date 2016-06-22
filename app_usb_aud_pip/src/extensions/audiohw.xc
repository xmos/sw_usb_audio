#include <xs1.h>
#include <platform.h>
#include <assert.h>
#include <print.h>

#include "devicedefines.h"
#include "i2c.h"

/* I2C ports */
struct r_i2c i2c = 
{
    on tile[0]: XS1_PORT_1M,    // SCL
    on tile[0]: XS1_PORT_1A     // SDA
};

on tile[0]: out port    p_dac_pdn = XS1_PORT_1D; /* DAC power down. Set low to hold DAC in power down state */

/* Device I2C Addresses */
#define AK4376_I2C_DEVICE_ADDR      (0x10)

/* SABRE9018Q2C Register Addresses */
#define AK4376_PWR_MGMT1    0x00 // Power Management 1
#define AK4376_PWR_MGMT2    0x01 // Power Management 2
#define AK4376_PWR_MGMT3    0x02 // Power Management 3
#define AK4376_PWR_MGMT4    0x03 // Power Management 4
#define AK4376_OUT_MODE     0x04 // Output Mode Setting
#define AK4376_CLK_MODE     0x05 // Clock Mode Select
#define AK4376_DIG_FILT     0x06 // Digital Filter Select
#define AK4376_MONO_MIX     0x07 // DAC Mono Mixing
#define AK4376_LCH_VOL      0x0B // Lch Output Volume
#define AK4376_RCH_VOL      0x0C // Rch Output Volume
#define AK4376_HP_VOL       0x0D // Headphone Volume Control
#define AK4376_PLL_CLK_SRC  0x0E // PLL Clock Source Select
#define AK4376_PLL_REF_DIV1 0x0F // PLL Ref Clk Divider 1
#define AK4376_PLL_REF_DIV2 0x10 // PLL Ref Clk Divider 2
#define AK4376_PLL_FB_DIV1  0x11 // PLL FB Clk Divider 1
#define AK4376_PLL_FB_DIV2  0x12 // PLL FB Clk Divider 2
#define AK4376_DAC_CLK_SRC  0x13 // DAC Clk Source
#define AK4376_DAC_CLK_DIV  0x14 // DAC Clk Divider
#define AK4376_AUDIO_IF     0x15 // Audio I/F Format
#define AK4376_MODE_CTRL    0x24 // Mode Control
#define AK4376_DAC_ADJ1     0x26 // DAC Adjustment 1
#define AK4376_DAC_ADJ2     0x2A // DAC Adjustment 2

/* AK4376 easy register access macros */
#define AK4376_REGREAD(reg, data)  {data[0] = 0xAA; i2c_master_read_reg(AK4376_I2C_DEVICE_ADDR, reg, data, 1, i2c);}
#define AK4376_REGWRITE(reg, val) {data[0] = val; i2c_master_write_reg(AK4376_I2C_DEVICE_ADDR, reg, data, 1, i2c);}

/* Wait a time specified in ms */
void wait_ms(unsigned wait_time)
{
  timer t;
  unsigned time;

  t :> time;
  time += (100000 * wait_time);
  t when timerafter(time) :> int _;
}


/* Bring DAC power supplies up*/
void DAC_start(void) 
{
  unsigned char data[1] = {0};

  i2c_master_init(i2c);
  
  AK4376_REGWRITE(AK4376_PWR_MGMT1      , 0x01); // Power up the PLL.
  wait_ms(10); // Wait 10ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x01); // Power up charge pump 1.
  wait_ms(7); // Wait 7ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x31); // Keep charge pump 1 on and turn on LDO1 supply.
  wait_ms(1); // Wait 1ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT3      , 0x01); // Power up the DAC.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x33); // Keep charge pump 1 and LDO1 on and turn on charge pump 2 supply.
  wait_ms(5); // Wait 5ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT4      , 0x07); // Power up both headphone output channels, no Class-G operation, supplies always at +-VDD.
  wait_ms(26); // Wait 26ms. 
  // DAC now ready to play audio samples.
  
} 

/* Take DAC power supplies down gracefully */
void DAC_stop(void) 
{
  unsigned char data[1] = {0};

  i2c_master_init(i2c);

  AK4376_REGWRITE(AK4376_PWR_MGMT4      , 0x04); // Both headphone outputs powered down, no Class-G operation, supplies always at +-VDD.
  wait_ms(5); // Wait 5ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT3      , 0x00); // Power down the DAC.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x31); // Keep charge pump 1 and LDO1 on and power down charge pump 2 supply. 
  wait_ms(1); // Wait 1ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x01); // Keep charge pump 1 on and power down LDO1 supply.
  wait_ms(7); // Wait 7ms.
  AK4376_REGWRITE(AK4376_PWR_MGMT2      , 0x00); // Controllable supplies now all powered off.  
  wait_ms(10); // Wait 10ms. 
  AK4376_REGWRITE(AK4376_PWR_MGMT1      , 0x00); // Power down the PLL.

  // DAC now ready to have PLL reprogrammed
  
} 

/* Configures initial DAC settings */
void AudioHwInit(chanend ?c_codec)
{
  unsigned char data[1] = {0};

  i2c_master_init(i2c);

  p_dac_pdn <: 1; // Take DAC out of power down mode.
  
  wait_ms(1); // Wait 1ms.
  
  AK4376_REGWRITE(AK4376_OUT_MODE     , 0x00); // HP Out pulled down by 6 ohm when disabled. Class-G VDD Mode Hold Time = 1024fs.
  AK4376_REGWRITE(AK4376_DIG_FILT     , 0x01); // Noise gate disable, Sharp roll off filter.
  AK4376_REGWRITE(AK4376_MONO_MIX     , 0x21); // No mixing, Normal polarity.
  AK4376_REGWRITE(AK4376_LCH_VOL      , 0x19); // 0dB Digital Volume for both channels.
  //AK4376_REGWRITE(AK4376_HP_VOL       , 0x09); // -4dB Headphone analogue volume.
  AK4376_REGWRITE(AK4376_HP_VOL       , 0x0B); // 0dB Headphone analogue volume.
  AK4376_REGWRITE(AK4376_PLL_CLK_SRC  , 0x00); // Sets MCLK pin as source for PLL.
  AK4376_REGWRITE(AK4376_PLL_REF_DIV1 , 0x00); // PLD[15:8] = 0x00 (PLL setting that does not change).
  AK4376_REGWRITE(AK4376_PLL_FB_DIV1  , 0x00); // PLM[15:8] = 0x00 (PLL setting that does not change).
  AK4376_REGWRITE(AK4376_DAC_CLK_SRC  , 0x01); // Sets DAC Master clock source as output from PLL.
  AK4376_REGWRITE(AK4376_DAC_CLK_DIV  , 0x04); // Sets DAC Master clock divider to divide by 5.
  AK4376_REGWRITE(AK4376_AUDIO_IF   , 0x10); // Sets Master mode, BCLK = 64Fs, I2S Interface, 24 bit data.
  AK4376_REGWRITE(AK4376_MODE_CTRL    , 0x00); // Sets DSMLP bit to 0 which is required for all non low power modes.  
  AK4376_REGWRITE(AK4376_DAC_ADJ1   , 0x20); // Unspecified "DAC Adjustment Setting"
  //AK4376_REGWRITE(AK4376_DAC_ADJ2   , 0x05); // Unspecified "DAC Adjustment Setting"
  AK4376_REGWRITE(AK4376_DAC_ADJ2   , 0x0F); // Unspecified "DAC Adjustment Setting". Allows tuning of THD. 0x0F gives <0.001%THD with no load. May need to tune for best performance driving low-z load (headphones)

  DAC_start();
} 


void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
  unsigned char data[1] = {0};

  DAC_stop();

  /* Sample frequency dependent register settings */
  if ((samFreq % 22050) == 0)
  {
    // 44.1,88.2,176.4kHz
    AK4376_REGWRITE(AK4376_PLL_REF_DIV2 , 0x1A);
    AK4376_REGWRITE(AK4376_PLL_FB_DIV2  , 0x7E);
    if (samFreq == 44100)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x29);
    }
    else if (samFreq == 88200)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x0D);
    }
    else if (samFreq == 176400)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x71);
    }
    else
    {
      printintln(samFreq);
      printstr("Unrecognised sample freq in ConfigCodec\n");
      assert(0);
    } 
  }
  else if ((samFreq % 24000) == 0) 
  {
    // 48,96,192kHz
    AK4376_REGWRITE(AK4376_PLL_REF_DIV2 , 0x18);
    AK4376_REGWRITE(AK4376_PLL_FB_DIV2  , 0x7F);
    if (samFreq == 48000)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x2A);
    }
    else if (samFreq == 96000)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x0E);
    }
    else if (samFreq == 192000)
    {
      AK4376_REGWRITE(AK4376_CLK_MODE   , 0x72);
    }
    else
    {
      printintln(samFreq);
      printstr("Unrecognised sample freq in ConfigCodec\n");
      assert(0);
    }
  }
  else
  {
    if (samFreq == 1234)
      return;
    printintln(samFreq);
    printstr("Unrecognised sample freq in ConfigCodec\n");
    assert(0);
  }

  DAC_start();

}
