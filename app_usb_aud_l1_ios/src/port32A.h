/**
 * @file        port32A.h
 * @brief       Port 32A access functions and bit defs for L1 USB Audio board 
 * @author      Ross Owen, XMOS Semiconductor 
 * @version     1.0
 * @date        30/01/2010
 */

#ifndef _PORT32A_OUT_
#define _PORT32A_OUT_ 

/* Bit defs */
#include "devicedefines.h"
#ifdef IO_EXPANSION
/* Outputs to port32A via shift register */
#define P32A_USB_RST       (1 << 3)   /* ULPI rst line */  
#define P32A_COD_RST       (1 << 4)   /* Codec rst line */
#define P32A_CLK_SEL       (1 << 5)   /* MClk Select line */
#define P32A_LED_A         (1 << 6)   /* LED A */
#define P32A_LED_B         (1 << 7)   /* LED B */
#define P32A_I2C_NOTMIDI   (1 << 0)   /* I2C !MIDI */
#define P32A_USB_SEL       (1 << 2)   /* High is 30pin, low is USB B */
#define P32A_ACC_DET_ID_EN (1 << 1)   /* Accessory detect - high means ready to talk to iOS dev */
/* Inputs to port32A via shift register */
#define P32A_IN_SW1         (1 << 0)   /* Switch 1 */
#define P32A_IN_SW2         (1 << 1)   /* Switch 2 */
#define P32A_IN_DEV_DETECT  (1 << 2)   /* Device detect */
#else
#define P32A_USB_RST       (1 << 0)   /* ULPI rst line */  
#define P32A_COD_RST       (1 << 1)   /* Codec rst line */
#define P32A_CLK_SEL       (1 << 2)   /* MClk Select line */
#define P32A_LED_A         (1 << 3)   /* LED A */
#define P32A_LED_B         (1 << 4)   /* LED B */
#define P32A_I2C_NOTMIDI   (1 << 6)   /* I2C !MIDI */
#endif

/* Outputs passed value to port 32A */
void port32A_out(int value);

/* Performs peek operation on port 32A and returns value on pins */
unsigned port32A_peek();

void port32A_set(int mask);
void port32A_unset(int mask);
void port32A_mask_and_set(int mask, int value);

#endif
