#include "devicedefines.h"
#include "expansion.h"
#include "port32A.h"

// Ensures that bits in mask are set to value
void port32A_mask_and_set(int mask, int value) {
#ifdef IO_EXPANSION
   expansion_io_mask_and_set(mask, value);
#else
   unsigned tmp = port32A_peek();
   tmp &= (~mask);
   tmp |= value;
   port32A_out(tmp);
#endif
}

// Set the bits in mask
void port32A_set(int mask) {
#ifdef IO_EXPANSION
   expansion_io_set(mask);
#else
   unsigned tmp = port32A_peek();
   tmp |= mask;
   port32A_out(tmp);
#endif
}

// Unset the bits in mask
void port32A_unset(int mask) {
#ifdef IO_EXPANSION
   expansion_io_unset(mask);
#else
   unsigned tmp = port32A_peek();
   tmp &= (~mask);
   port32A_out(tmp);
#endif
}


