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
#define P32A_USB_RST       0x01           /* ULPI rst line */  
#define P32A_COD_RST       0x02           /* Codec rst line */
#define P32A_CLK_SEL       0x04           /* MClk Select line */
#define P32A_LED_A         0x08           /* LED A */
#define P32A_LED_B         0x10           /* LED B */

/* Outputs passed value to port 32A */
void port32A_out(int value);

/* Performs peek operation on port 32A and returns value on pins */
unsigned port32A_peek();

#endif
