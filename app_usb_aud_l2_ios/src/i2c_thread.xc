/**
 * Module:  app_usb_aud_l2
 * Version: 5v11_iosrc0
 * Build:   fd8b431141850fdbe187f949cc0c7da2408d139c
 * File:    i2c_thread.xc
 *
 * The copyrights, all other intellectual and industrial 
 * property rights are retained by XMOS and/or its licensors. 
 * Terms and conditions covering the use of this code can
 * be found in the Xmos End User License Agreement.
 *
 * Copyright XMOS Ltd 2010
 *
 * In the case where this code is a modification of existing code
 * under a separate license, the separate license terms are shown
 * below. The modifications to the code are still covered by the 
 * copyright notice above.
 *
 **/                                   
#include "iic.h"
#include "print.h"

timer i2ctimer;

void i2c_sf(chanend source, unsigned isWrite, port p_scl, port p_sda)
{
    {
         if (isWrite) {
            int device, addr;
            int data;
            int len = 1;
            char data_arr[2000];
            int retVal = 0;
            source :> device;
            source :> addr;
            source :> len;
            //printf("I2C write device: 0x%04x, address: 0x%04x, data: 0x%02x\n", device, addr, data);
            for(int i = 0; i != len; i++) {
               source :> data;
               data_arr[i] = data;
            }
            retVal = iic_write(device >> 1, addr, data_arr, len, i2ctimer, p_scl, p_sda);
            source <: retVal;
            //printf("I2C write c\n");
         } else {
            int device, addr;
            int data;
            int len = 1;
            char data_arr[2000]; // Think that iic_read uses 1 more byte than numBytes
            int retVal = 0;
            source :> device;
            source :> addr;
            source :> len;
            //printf("I2C read\n");
            retVal = iic_read(device >> 1, addr, data_arr, len, i2ctimer, p_scl, p_sda);
            for(int i = 0; i != len; i++) {
               data = data_arr[i];
               source <: data;
            }
            source <: retVal;
            //printf("I2C read device: 0x%04x, address: 0x%04x, data: 0x%02x\n", device, addr, data);
#if 0
            if(device != 0x9c && addr == 4)
            {
                printstr("I2C read device: ");
                printhex(device);
                printstr(", address: ");
                printhex(addr);
                printstr(", data: ");
                printhex(data);
                printstr("retval: ");
                printintln(retVal);
            }
#endif
         }
       }
}

void i2c_thread(chanend thread1, chanend thread2, port p_scl, port p_sda) 
{
    iic_initialise(i2ctimer, p_scl, p_sda);
    while(1) 
    {
        unsigned isWrite;
        select 
        {
            /* Can't use select fuction as want to pass in ports aswell...*/
            //case i2c_sf(thread1, isWrite, p_scl, p_sda);
            //case i2c_sf(thread2, isWrite, p_scl, p_sda);
            case thread1 :> isWrite:
                i2c_sf(thread1, isWrite, p_scl, p_sda);
                break;

            case thread2 :> isWrite:
                i2c_sf(thread2, isWrite, p_scl, p_sda);
                break;
        }
    }
}


