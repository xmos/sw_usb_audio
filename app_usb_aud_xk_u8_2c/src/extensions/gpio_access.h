#ifndef _GPIO_ACCESS_H_
#define _GPIO_ACCESS_H_
#include <xccompat.h>

void port32A_lock();
void port32A_unlock();
void port32A_lock_peek(REFERENCE_PARAM(unsigned, x));
void port32A_out_unlock(unsigned x);

#endif
