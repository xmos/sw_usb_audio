
#ifdef USB_SEL_A

#include <interrupt.h>

register_interrupt_handler(HandleRebootTimeout, 1, 200)

#endif
