#include <platform.h>
#include <xs1.h>
#include "gpio.h"
#include "print.h"

#define VERIFY_I2C 1

void set_gpio(out port p_gpio, unsigned bit, unsigned value)
{
	unsigned port_shadow;
	port_shadow = peek(p_gpio);         //Read port pin value
	if (value == 0) port_shadow &= ~bit;//If writing a 0, generate mask and AND with current val
	else port_shadow |= bit;            //Else use mask and OR to set bit
	p_gpio <: port_shadow;              //Write back to port. Will make port an output if not already
}

void wait_us(int microseconds)
{
    timer t;
    int time;

    t :> time;
    t when timerafter (time + (microseconds * 100)) :> void;
}


int i2c_slave_configure(int codec_addr, int num_writes,
		                unsigned char reg_addr[], unsigned char reg_data[],
#if I2C_COMBINE_SCL_SDA
                        port r_i2c
#else
                        struct r_i2c &r_i2c
#endif
                        ){
// Unfortunately the single port and simple I2C APIs do not currently match
// with regards the device address. This works around it
#if I2C_COMBINE_SCL_SDA
     codec_addr <<= 1;
#endif
    int success = 1;
    unsigned char data[1];
    i2c_master_init(r_i2c);
    for(int i = 0; i < num_writes; i++){
        data[0] = reg_data[i];
        success &= i2c_master_write_reg(codec_addr, reg_addr[i], data, 1, r_i2c);
#if VERIFY_I2C==1
        if (success == 0) {
            printstr("ACK failed on I2C write to device 0x");
            printhex(codec_addr);
            printstr(", reg address 0x");
            printhexln(reg_addr[i]);
        }
        i2c_master_read_reg(codec_addr, reg_addr[i], data, 1, r_i2c);
        if (data[0] != reg_data[i]){
            printstr("ERROR");
            printstr(" verifying I2C device 0x");
            printhex(codec_addr);
            printstr(" register address 0x");
            printhex(reg_addr[i]);
            printstr(". Expected 0x");
            printhex(reg_data[i]);
            printstr(", received 0x");
            printhexln(data[0]);
        }
#endif
    }
    return(success);
}

