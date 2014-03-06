
#include "platform.h"
#include "devicedefines.h"
#include <print.h>

#ifdef HID_CONTROLS

/* Write HID Report Data into hidData array
 *
 * Bits are as follows:
 * 0: Play/Pause
 * 1: Scan Next Track
 * 2: Scan Prev Track
 * 3: Volume Up
 * 4: Volime Down
 * 5: Mute
 */



void UserReadHIDButtons(unsigned char hidData[])
{

}

#endif
