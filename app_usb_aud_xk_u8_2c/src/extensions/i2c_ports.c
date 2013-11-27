#include <platform.h>
#include "i2c_shared.h"

/* I2C ports */
struct r_i2c i2cPorts = {PORT_I2C_SCL, PORT_I2C_SDA}; /* In a struct to use module_i2c_simple */