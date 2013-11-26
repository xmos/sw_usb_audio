#ifndef _GPIO_ACCESS_H_
#define _GPIO_ACCESS_H_
#include <xccompat.h>

void port32A_peek(REFERENCE_PARAM(unsigned, x));
void port32A_out(unsigned x);

#endif
