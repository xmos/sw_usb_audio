/* Functions that must be implemented by vendor for board support purposes 
 * 
 * Implementation for XS-IOS-USB-AUDIO board - Uses shift registers 
 *
 */

#include "port32A.h"
#include "expansion.h"

/* Enable/Power-on/Reset etc coProcessor - called before authentication */
void CoProcessorEnable(void)
{
    port32A_set(P32A_I2C_NOTMIDI);
}

/* Disable co-processor - Called at end of authentication */
void CoProcessorDisable(void)
{
    port32A_unset(P32A_I2C_NOTMIDI);
}

/* Select Apple 30 pin connector */
void SelectUSBDock(void)
{
    port32A_set(P32A_USB_SEL); // USB SEL low
}

/* Select USB socket (normally B) */
void SelectUSBPc(void)
{
    port32A_unset(P32A_USB_SEL); // USB SEL high
}

/* Return iDevice detect state, return zero for detected */
unsigned GetIDeviceDetect(void)
{
    return expansion_io_peek() & P32A_IN_DEV_DETECT;
}
