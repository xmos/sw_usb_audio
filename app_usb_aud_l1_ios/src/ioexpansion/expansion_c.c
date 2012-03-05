#include <print.h>
#include <xccompat.h>
#include "expansion.h"
#include "lock.h"
#include "xc_ptr.h"

extern port p_usb_rst;
#define p p_usb_rst
unsigned g_output = 0; // Saved state of output
lock g_lock;

void expansion_io_init() {
   lock l = GetLockResource();
   SET_SHARED_GLOBAL(g_lock, l);
}

void expansion_io_deinit() {
   lock l;
   GET_SHARED_GLOBAL(l, g_lock);
   FreeLockResource(l);
}

// Ensure bits in mask are set to value
void expansion_io_mask_and_set(unsigned mask, unsigned value) {
   unsigned output;
   unsigned newoutput;
   lock l;
   GET_SHARED_GLOBAL(l, g_lock);
   ClaimLock(l);
   GET_SHARED_GLOBAL(output, g_output);
   newoutput = output;
   newoutput &= ~mask;
   newoutput |= value;
   if (newoutput != output) {
      expansion_o_byte(newoutput, p);
      SET_SHARED_GLOBAL(g_output, newoutput);
   }
   FreeLock(l);
}

// Set the bits in mask
void expansion_io_set(unsigned mask) {
   unsigned output;
   unsigned newoutput;
   lock l;
   GET_SHARED_GLOBAL(l, g_lock);
   ClaimLock(l);
   GET_SHARED_GLOBAL(output, g_output);
   newoutput = output;
   newoutput |= mask;
   if (newoutput != output) {
      expansion_o_byte(newoutput, p);
      SET_SHARED_GLOBAL(g_output, newoutput);
   }
   FreeLock(l);
}

// Unset the bits in mask
void expansion_io_unset(unsigned mask) {
   unsigned output;
   unsigned newoutput;
   lock l;
   GET_SHARED_GLOBAL(l, g_lock);
   ClaimLock(l);
   GET_SHARED_GLOBAL(output, g_output);
   newoutput = output;
   newoutput &= ~mask;
   if (newoutput != output) {
      expansion_o_byte(newoutput, p);
      SET_SHARED_GLOBAL(g_output, newoutput);
   }
   FreeLock(l);
}

// Read the input shift register
unsigned expansion_io_peek() {
   unsigned output;
   unsigned input;
   lock l;
   GET_SHARED_GLOBAL(l, g_lock);
   ClaimLock(l);
   GET_SHARED_GLOBAL(output, g_output);
   input = expansion_io_byte(output, p);
   FreeLock(l);
   return input;
}


