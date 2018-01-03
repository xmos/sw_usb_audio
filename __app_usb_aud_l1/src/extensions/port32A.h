/**
 * @file        port32A.h
 * @brief       Port 32A bit defines for L1 USB Audio board
 * @author      Ross Owen, XMOS Semiconductor
 */

#ifndef _PORT32A_OUT_
#define _PORT32A_OUT_

/* Bit defs */
#define P32A_USB_RST       0x01           /* ULPI rst line */
#define P32A_COD_RST       0x02           /* Codec rst line */
#define P32A_CLK_SEL       0x04           /* MClk Select line */
#define P32A_LED_A         0x08           /* LED A */
#define P32A_LED_B         0x10           /* LED B */

#endif
