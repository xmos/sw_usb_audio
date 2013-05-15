
extern in port p_but_a;
extern in port p_but_b;

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
    hidData[0] = (a << 3) | (b << 4);
#endif
}
