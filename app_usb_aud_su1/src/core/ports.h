#ifndef _PORTS_H_
#define _PORTS_H_
#include "i2c.h"

/* Additional ports used in this application instance */
on stdcore[0] : out port p_gpio     = PORT_GPIO;
on stdcore[0] : struct r_i2c i2cPorts = {PORT_I2C_SCL, PORT_I2C_SDA}; /* In a struct to use module_i2c_simple */
on stdcore[0] : in port p_but       = PORT_BUT;

#endif
