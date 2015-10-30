#ifndef _CS5368_H_
#define _CS5368_H_

//Address on I2C bus
#define CS5368_I2C_ADDR      (0x4C)

//Register Addresess
#define CS5368_CHIP_REV      0x00
#define CS5368_GCTL_MDE      0x01
#define CS5368_OVFL_ST       0x02
#define CS5368_OVFL_MSK      0x03
#define CS5368_HPF_CTRL      0x04
#define CS5368_PWR_DN        0x06
#define CS5368_MUTE_CTRL     0x08
#define CS5368_SDO_EN        0x0a

#endif /* _CS5368_H_ */
