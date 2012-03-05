/**
 * Module:  app_usb_aud_l2
 * Version: 5v11_iosrc0
 * Build:   5f9730b10fe114a152378e8036adc50e6fc625fc
 * File:    i2c_thread.h
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
#ifndef I2C_THREAD_H
#define I2C_THREAD_H
void i2c_thread(chanend thread1, chanend thread2, port p_scl, port p_sda);
#endif // I2C_THREAD_H
