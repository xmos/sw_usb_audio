#ifndef _CS5368_H_
#define _CS5368_H_

//Address on I2C bus
#define CS5368_I2C_ADDR      0x4C

//Register Addresess
#define CS5368_CHIP_REV      0x00
#define CS5368_GCTL_MDE      0x01
#define CS5368_OVFL_ST       0x02
#define CS5368_OVFL_MSK      0x03
#define CS5368_HPF_CTRL      0x04
#define CS5368_PWR_DN        0x06
#define CS5368_MUTE_CTRL     0x08
#define CS5368_SDO_EN        0x0a

//Default values used in this application
#define CS5368_CHIP_REV_VAL  0x81 //CS5368 Rev B of the chip
#define CS5368_GCTL_MDE_VAL  0x97 //Enable control port, /2 mclk, I2S format, slave mode autodetect speed
#define CS5368_OVFL_ST_VAL   0xff //No overflows (read only)
#define CS5368_OVFL_MSK_VAL  0xff //enable all overflow interrupts
#define CS5368_HPF_CTRL_VAL  0x00 //disable HPF
#define CS5368_PWR_DN_VAL    0x00 //Everything powered up
#define CS5368_MUTE_CTRL_VAL 0x00 //Mute off all channels
#define CS5368_SDO_EN_VAL    0x00 //SDO pins enabled

#endif /* _CS5368_H_ */
