#include <xs1.h>
#include <platform.h>

#include "devicedefines.h"
#include "user_hid.h"

#ifndef MIDI
/* MIDI shared with button pins */
on tile[0] : in port p_but_a = XS1_PORT_1J;
on tile[0] : in port p_but_b = XS1_PORT_1K;
#endif

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
#ifndef MIDI
    unsigned a, b;

    p_but_a :> a;
    p_but_b :> b;

    a = (~a) & 1;
    b = (~b) & 1;

    /* Assign buttons A and B to Vol Up/Down */
    hidData[0] = (a << HID_CONTROL_VOLUP_SHIFT) | (b << HID_CONTROL_VOLDN_SHIFT);
#endif
}
#endif // HID_CONTROLS
