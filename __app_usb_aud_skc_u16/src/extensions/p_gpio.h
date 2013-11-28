/**
 * @file        p_gpio.h
 * @brief       Port access functions to the port p_gpio
 * @author      Ross Owen, XMOS Semiconductor
 * @version     1.0
 * @date        30/01/2010
 */

#ifndef _P_GPIO_
#define _P_GPIO_

/* Outputs passed value to port p_gpio */
void p_gpio_out(int value);

/* Performs peek operation on port p_gpio and returns value on pins */
unsigned p_gpio_peek();

#endif
