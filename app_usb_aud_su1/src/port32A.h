/**
 * @file        port32A.h
 * @brief       Port 32A access functions and bit defs for L1 USB Audio board 
 * @author      Ross Owen, XMOS Semiconductor 
 * @version     1.0
 * @date        30/01/2010
 */

#ifndef _PORT32A_OUT_
#define _PORT32A_OUT_ 

/* General output port bit definitions */
#define P32A_COD_RST_N     0x01    /* CODEC reset. Active low. */
#define P32A_MCLK_SEL      0x02    /* MCLK frequency select. 0 - 22.5792MHz, 1 - 24.576MHz */
#define P32A_PWR_EN_N      0x04    /* +5V Power Enable. Active low. */
#define P32A_LED_A         0x08    /* LED A. Active high */
#define P32A_LED_B         0x10    /* LED B. Active high */

/* Outputs passed value to port 32A */
void port32A_out(int value);

/* Performs peek operation on port 32A and returns value on pins */
unsigned port32A_peek();

#endif
