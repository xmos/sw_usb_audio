#ifndef EXPANSION_H
#define EXPANSION_H
#include <xccompat.h>
// High level access functions. Handle lock and persistence of output value.
void expansion_io_init(void);
void expansion_io_deinit(void);
void expansion_io_set(unsigned);
void expansion_io_mask_and_set(unsigned, unsigned);
void expansion_io_unset(unsigned);
unsigned expansion_io_peek();
// Low level access function. 
unsigned expansion_io_byte(int data_out, port p);
void expansion_o_byte(int data_out, port p);
#endif
