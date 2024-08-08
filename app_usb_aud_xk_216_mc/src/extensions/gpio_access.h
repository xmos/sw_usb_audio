#ifndef _GPIO_ACCESS_H_
#define _GPIO_ACCESS_H_

#include "app_usb_aud_xk_216_mc.h"

#include <platform.h>

void set_gpio(unsigned bit, unsigned value);
void p_gpio_lock();
void p_gpio_unlock();
unsigned p_gpio_peek();
void p_gpio_out(unsigned x);

#endif
