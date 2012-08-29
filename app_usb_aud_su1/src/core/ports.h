#ifndef _PORTS_H_
#define _PORTS_H_

/* Additional ports used in this application instance */
on stdcore[0] : out port p_gpio     = PORT_GPIO;
on stdcore[0] : port p_i2c_sda      = PORT_I2C_SDA;
on stdcore[0] : port p_i2c_scl      = PORT_I2C_SCL;
on stdcore[0] : in port p_but       = PORT_BUT;

#endif
