#ifndef CS4384_H_
#define CS4384_H_

//Address on I2C bus
#define CS4384_I2C_ADDR      (0x18)

//Register Addresess
#define CS4384_CHIP_REV      0x01
#define CS4384_MODE_CTRL     0x02
#define CS4384_PCM_CTRL      0x03
#define CS4384_DSD_CTRL      0x04
#define CS4384_FLT_CTRL      0x05
#define CS4384_INV_CTRL      0x06
#define CS4384_GRP_CTRL      0x07
#define CS4384_RMP_MUTE      0x08
#define CS4384_MUTE_CTRL     0x09
#define CS4384_MIX_PR1       0x0a
#define CS4384_VOL_A1        0x0b
#define CS4384_VOL_B1        0x0c
#define CS4384_MIX_PR2       0x0d
#define CS4384_VOL_A2        0x0e
#define CS4384_VOL_B2        0x0f
#define CS4384_MIX_PR3       0x10
#define CS4384_VOL_A3        0x11
#define CS4384_VOL_B3        0x12
#define CS4384_MIX_PR4       0x13
#define CS4384_VOL_A4        0x14
#define CS4384_VOL_B4        0x15
#define CS4384_CM_MODE       0x16

#endif /* CS4384_H_ */
