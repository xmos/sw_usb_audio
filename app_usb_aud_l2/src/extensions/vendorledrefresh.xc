/*
 * lvlleds.xc
 *
 * Interface to optional extra LED board
 *
 */
#include <xclib.h>
#include <xs1.h>
#include <platform.h>
#include "devicedefines.h"

#define NUM_LED_SHIFT_REGS 6

unsigned data[NUM_LED_SHIFT_REGS];
unsigned lvldata[NUM_USB_CHAN_IN];

unsigned peaklvlcount[NUM_LED_SHIFT_REGS];
unsigned ledcount = 0;

on tile[1] : out port p_gpio = PORT_GPIO;

#define SHIFT_REG_DAT 1 // Data
#define SHIFT_REG_CLK 2 // CLock
#define SHIFT_REG_LAT 4 // Latch
#define SHIFT_REG_OE  8

static inline void shiftOut(out port p_gpio, unsigned data)
{
    unsigned tmp;

#pragma loop unroll
    for (int i = 7; i >= 0; i--)
    {
        p_gpio <: 0;
        p_gpio <: 0;

        tmp = data >> i;
        tmp &= SHIFT_REG_DAT;

        p_gpio <: tmp;
        p_gpio <: tmp;

        tmp |= SHIFT_REG_CLK;

        p_gpio <: tmp;
        p_gpio <: tmp;
    }
    p_gpio <: 0;
    p_gpio <: 0;
}

#pragma unsafe arrays
void WriteToLEDShiftRegs(out port p_gpio, unsigned data[], unsigned length)
{
    p_gpio <: 0;
    for(int i = 0; i < length; i++)
    {
        shiftOut(p_gpio, data[i]);
    }

    p_gpio <: SHIFT_REG_LAT ;
}

#pragma unsafe arrays
void VendorLedRefresh(unsigned levelData[])
{
	WriteToLEDShiftRegs(p_gpio, data, NUM_LED_SHIFT_REGS);

    ledcount++;
    /* We dont need to update the lvls everytime we refresh leds.. */
    if(ledcount==20)
    {
        unsigned tmp;
        ledcount = 0;

        for(int i = 0; i < NUM_LED_SHIFT_REGS; i++)
        {
            lvldata[i] = 32 - clz(levelData[i]>>23);
            asm("mkmsk %0, %1" : "=r" (tmp): "r" (lvldata[i]));

            peaklvlcount[i] |= (tmp & 0x80);

            if(peaklvlcount[i])
                tmp|= 0x80;

            peaklvlcount[i] >>= 1;

            data[i] = tmp ;
        }
    }
}
