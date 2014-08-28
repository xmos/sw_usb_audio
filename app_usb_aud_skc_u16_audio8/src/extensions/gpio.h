#ifndef _GPIO_H_
#define _GPIO_H_
#include "i2c.h"

/* General output port bit definitions (port 4D, PORT_PWR_PLL_MUTE) */
#define P_VA_EN                 0x1    /* 1 = 5V analog and 2v5 ADC digital supply enable */
#define P_PLL_SEL               0x2    /* 1 = CS2100, 0 = Phaselink clock source */
#define P_MUTE_A                0x4    /* Mute A signal - Brought out to header only*/
#define P_MUTE_B                0x8    /* Mute B signal - Brought out to header only*/


/* General output port bit definitions (port 4E, PORT_ADRST_CKSEL_DSD) */
#define P_DAC_RST_N             0x1    /* 0 = Reset ADC */
#define P_ADC_RST_N             0x2    /* 0 = Reset DAC */
#define P_F_SELECT              0x4    /* Select frequency on Phaselink clock. 0 = 24.576MHz for 48k, 1 = 22.5792MHz for 44.1k.*/
#define P_DSD_MODE              0x8    /* DSD mode select 0 = 8i/8o I2S, 1 = 8o DSD*/

/*LED array defines*/
#define LED_ALL_ON              0xf00f
#define LED_SQUARE_BIG          0x9009
#define LED_SQUARE_SML          0x6006
#define LED_ROW_1               0xf001
#define LED_ROW_2               0xf003
#define LED_ROW_3               0xf007
#define ALL_OFF                 0x0000
// LED array masks
#define LED_MASK_COL_OFF        0x7fff
#define LED_MASK_DISABLE        0xffff

#if __XC__
void set_gpio(out port p_gpio, unsigned bit, unsigned value);

void wait_us(int microseconds);



int i2c_slave_configure(int codec_addr, int num_writes,
		              unsigned char reg_addr[], unsigned char reg_data[],
#if I2C_COMBINE_SCL_SDA
                      port r_i2c
#else
                      struct r_i2c &r_i2c
#endif
                      );

void i2c_slave_verify(int codec_addr, int num_writes,
		              unsigned char reg_addr[], unsigned char reg_data[],
#if I2C_COMBINE_SCL_SDA
                      port r_i2c
#else
                      struct r_i2c &r_i2c
#endif
                      );
#endif /* __XC__ */

void set_led_array(unsigned short led_pattern);

void set_led_array_mask(unsigned short led_mask);

unsigned short get_led_array_mask();

#endif //_GPIO_H_
