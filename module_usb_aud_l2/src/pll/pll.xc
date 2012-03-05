#include <platform.h>
#include <assert.h>
#include "iic.h"
#define DEV_ADR      (0x9C  >>1) 

#include "iicports.h"

int readReg(unsigned devAdr, unsigned reg, chanend c)
{
    unsigned char data[1] = {0};
    iic_readC(devAdr, reg, data, 1, c, p_i2c_scl, p_i2c_sda);
    return data[0];
}

#define PLL_REGRD(reg) 		readReg(DEV_ADR, reg, c)
#define PLL_REGWR(reg, val) {data[0] = val; iic_writeC(DEV_ADR, reg, data, 1, c, p_i2c_scl, p_i2c_sda);}


/* Init of CS2300 */
void PllInit(chanend ?c)
{
    unsigned char data[1] ={0};
	/* Enable init */
    PLL_REGWR(0x03, 0x07);
    PLL_REGWR(0x05, 0x01);
    PLL_REGWR(0x16, 0x10);
    PLL_REGWR(0x17, 0x00); // 0x10 Always gen clock even when unlocked

  	/* Check */
	assert(PLL_REGRD(0x03) == 0x07);
    assert(PLL_REGRD(0x05) == 0x01);
    assert(PLL_REGRD(0x16) == 0x10);
    assert(PLL_REGRD(0x17) == 0x00);
}

/* Setup PLL multiplier */
void PllMult(unsigned mult, chanend ?c)
{
    unsigned char data[1] ={0};

	/* Multiplier is translated to 20.12 format by shifting left by 12 */
  	PLL_REGWR(0x06, (mult >> 12) & 0xFF);
  	PLL_REGWR(0x07, (mult >> 4) & 0xFF);
  	PLL_REGWR(0x08, (mult << 4) & 0xFF);
  	PLL_REGWR(0x09, 0x00);

	/* Check */
	assert(PLL_REGRD(0x06) == ((mult >> 12) & 0xFF));
    assert(PLL_REGRD(0x07) == ((mult >> 4) & 0xFF));
    assert(PLL_REGRD(0x08) == ((mult << 4) & 0xFF));
    assert(PLL_REGRD(0x09) == 0x00);
}


