
#include <xs1.h>
#include <platform.h>

#include "app_usb_aud_xk_216_mc.h"
#include "user_hid.h"
#include "xua_hid_report.h"

#if HID_CONTROLS > 0
in port p_sw = on tile[XUD_TILE] : XS1_PORT_4B;

#define P_GPI_BUTA_SHIFT        0x00
#define P_GPI_BUTA_MASK         (1<<P_GPI_BUTA_SHIFT)
#define P_GPI_BUTB_SHIFT        0x01
#define P_GPI_BUTB_MASK         (1<<P_GPI_BUTB_SHIFT)
#define P_GPI_BUTC_SHIFT        0x02
#define P_GPI_BUTC_MASK         (1<<P_GPI_BUTC_SHIFT)
#define P_GPI_SW1_SHIFT         0x03
#define P_GPI_SW1_MASK          (1<<P_GPI_SW1_SHIFT)

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

typedef enum
{
	STATE_IDLE = 0x00,
	STATE_PLAY = 0x01,
	STATE_NEXTPREV = 0x02,
}t_controlState;

t_controlState state;

unsigned lastA;

static unsigned char lastHidData;

void UserHIDPoll()
{
    state = STATE_IDLE;

    while (1) {
        delay_milliseconds(HIDBUTTONS_POLL_MS);

        if (hidIsChangePending(0))
            continue;

        /* Variables for buttons a, b, c and switch sw */
        unsigned a, b, c, sw, tmp;

        p_sw :> tmp;

        /* Buttons are active low */
        tmp = ~tmp;

        a = (tmp & (P_GPI_BUTA_MASK))>>P_GPI_BUTA_SHIFT;
        b = (tmp & (P_GPI_BUTB_MASK))>>P_GPI_BUTB_SHIFT;
        c = (tmp & (P_GPI_BUTC_MASK))>>P_GPI_BUTC_SHIFT;
        sw = (tmp & (P_GPI_SW1_MASK))>>P_GPI_SW1_SHIFT;

        unsigned char hidData = 0;

        if(sw)
        {
            /* Assign buttons A and B to Vol Down/Up */
            hidData |= a * HID_CONTROL_VOLDN;
            hidData |= b * HID_CONTROL_VOLUP;
            hidData |= c * HID_CONTROL_MUTE;
        }
        else
        {
            /* Assign buttons A and B to play for single tap, next/prev for double tap */
            if(b)
            {
                multicontrol_count++;
                wait_counter = 0;
                lastA = 0;
            }
            else if(a)
            {
                multicontrol_count++;
                wait_counter = 0;
                lastA = 1;
            }
            else
            {
                if(multicontrol_count > THRESH)
                {
                    state++;
                }

                wait_counter++;

                if(wait_counter > (MULTIPRESS_WAIT_MS / HIDBUTTONS_POLL_MS))
                {
                    if(state == STATE_PLAY)
                    {
                        hidData = HID_CONTROL_PLAYPAUSE;
                    }
                    else if(state == STATE_NEXTPREV)
                    {
                        if(lastA)
                            hidData = HID_CONTROL_PREV;
                        else
                            hidData = HID_CONTROL_NEXT;
                    }
                    state = STATE_IDLE;
                }
                multicontrol_count = 0;
            }
        }

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
