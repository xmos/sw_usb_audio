
#ifndef _PORTS_H_
#define _PORTS_H_

#include "i2c.h"

/* Additional ports used in this application instance */

/* General Purpose Output port - various output lines such as DAC reset, LEDs etc */
on stdcore[0] : out port p_gpo  = XS1_PORT_32A;

/* Input port for buttons and switch */
on stdcore[0] : in port p_sw    = XS1_PORT_4D;

/* Output port for DAC/ADC reset lines, also has DSD Mode */
on stdcore[0] : out port p_audrst = XS1_PORT_4C;

/* I2C ports */
on stdcore[0] : struct r_i2c i2cPorts = {XS1_PORT_1C, XS1_PORT_1G}; /* In a struct to use module_i2c_simple */


#endif
