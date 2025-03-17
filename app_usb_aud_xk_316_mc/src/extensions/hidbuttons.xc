// Copyright 2013-2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

#include <xs1.h>
#include <platform.h>

#include "user_hid.h"
#include "xua_hid_report.h"
#include "xua_conf_full.h"

#if HID_CONTROLS > 0
in port p_sw = on tile[XUD_TILE] : XS1_PORT_4E;

#define P_GPI_BUTA_SHIFT        0x00
#define P_GPI_BUTA_MASK         (1<<P_GPI_BUTA_SHIFT)
#define P_GPI_BUTB_SHIFT        0x01
#define P_GPI_BUTB_MASK         (1<<P_GPI_BUTB_SHIFT)
#define P_GPI_BUTC_SHIFT        0x02
#define P_GPI_BUTC_MASK         (1<<P_GPI_BUTC_SHIFT)

/* Write HID Report Data into hidData array
 *
 * Bits are as follows:
 * 0: Play/Pause
 * 1: Scan Next Track
 * 2: Scan Prev Track
 * 3: Volume Up
 * 4: Volume Down
 * 5: Mute
 */

unsigned multicontrol_count = 0;
unsigned wait_counter =0;


#define THRESH 1
#define MULTIPRESS_WAIT_MS 200
#define HIDBUTTONS_POLL_MS   1

#define HID_CONTROL_PLAYPAUSE   0x01
#define HID_CONTROL_NEXT        0x02
#define HID_CONTROL_PREV        0x04
#define HID_CONTROL_VOLUP       0x08
#define HID_CONTROL_VOLDN       0x10
#define HID_CONTROL_MUTE        0x20

unsigned lastA;

static unsigned char lastHidData;

void UserHIDPoll()
{
    while (1) {
        delay_milliseconds(HIDBUTTONS_POLL_MS);

        if (hidIsChangePending(0))
            continue;

        /* Variables for buttons a, b, c */
        unsigned a, b, c, tmp;

        p_sw :> tmp;

        /* Buttons are active low */
        tmp = ~tmp;

        a = (tmp & (P_GPI_BUTA_MASK))>>P_GPI_BUTA_SHIFT;
        b = (tmp & (P_GPI_BUTB_MASK))>>P_GPI_BUTB_SHIFT;
        c = (tmp & (P_GPI_BUTC_MASK))>>P_GPI_BUTC_SHIFT;

        unsigned char hidData = 0;
        /* Assign buttons A and B to Vol Down/Up */
        hidData |= a * HID_CONTROL_VOLDN;
        hidData |= b * HID_CONTROL_VOLUP;
        hidData |= c * HID_CONTROL_MUTE;

        if (hidData == lastHidData)
            continue;

        unsafe {
            volatile unsigned char * unsafe lastHidDataUnsafe = &lastHidData;
            *lastHidDataUnsafe = hidData;
            hidSetChangePending(0);
        }
    }
}

size_t UserHIDGetData( const unsigned id, unsigned char hidData[ HID_MAX_DATA_BYTES ])
{
    // There is only one report, so the id parameter is ignored

    hidData[0] = lastHidData;

    // One byte of data is always returned
    return 1;
}

void UserHIDInit( void )
{
}

#endif  // HID_CONTROLS > 0
