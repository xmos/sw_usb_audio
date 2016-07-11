#include <platform.h>
#include <xs1.h>
#include "devicedefines.h"
#include "gpio_defines.h"
#include "user_hid.h"
#include "print.h"

#ifdef HID_CONTROLS
/* Buttons are on bit 0..2. Active high */
on tile[0]: in port p_buttons = XS1_PORT_8C;

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

#define PUSHED_THRESHOLD_16MS        1  //Debounce period
#define RELEASED_THRESHOLD_16MS      17 //Double tap period
#define LONG_PRESS_THRESHOLD_16MS    33 //How long until button is seen as held

typedef enum
{
    STATE_IDLE = 0,
    STATE_FIRST_PRESS = 1,
    STATE_FIRST_RELEASE = 2,
    STATE_SECOND_PRESS = 3,
    STATE_SECOND_RELEASE = 4,
    STATE_HOLD = 5,
    STATE_HOLD_RELEASE = 6
}t_controlState;

t_controlState state = STATE_IDLE;


void UseHIDInit(void)
{
    set_port_pull_down(p_buttons);  //Buttons are active high with no external pull down
}

//Helper function to set flags for given button pushes
static void extract_buttons(unsigned buttons, unsigned &but_vol_d, unsigned &but_pp, unsigned &but_vol_u)
{
    but_vol_d = (buttons & (P_GPIO_VOL_DOWN)) ? 1 : 0;
    but_pp = (buttons & (P_GPIO_PLAY_PAUSE)) ? 1 : 0;
    but_vol_u = (buttons & (P_GPIO_VOL_UP)) ? 1 : 0;
}

//This function is called every bInterval=8 -> 16 milliseconds
void UserReadHIDButtons(unsigned char hidData[])
{
    /* Flags for the buttons */
    unsigned but_vol_d, but_pp, but_vol_u, but_now;
    static unsigned but_last, but_current;
    static unsigned state_counter_ms = 0;

    p_buttons :> but_now;                // Read port

    extract_buttons(but_now, but_vol_d, but_pp, but_vol_u);

    if(but_vol_d || but_vol_u || but_pp) // Any button has been pressed
    {
        if (but_last != but_now)         // Is it a newly pressed?
        {
            state_counter_ms = 0;
            if (state == STATE_FIRST_PRESS) // First time this press has been seen
            {
                but_current = but_now;
            }
            if (state == STATE_SECOND_PRESS)
            {
                // Do nothing
            }
        }
        else                        // Has been held for a while
        {
            if (state_counter_ms == PUSHED_THRESHOLD_16MS) // Has been pressed long enough to be seen as a press
            {
                but_current = but_now;
                state++;
                if (state == (STATE_SECOND_PRESS + 4)) state -= 4;    // Allow multiple double taps
                if (state == STATE_SECOND_PRESS)                      // Second tap detected
                {
                    hidData[0] = ((but_vol_d << HID_CONTROL_PREV_SHIFT) | (but_vol_u << HID_CONTROL_NEXT_SHIFT) | (but_pp << HID_CONTROL_PLAYPAUSE_SHIFT));
                }
            }
            if (state_counter_ms > LONG_PRESS_THRESHOLD_16MS) // Has been held a while
            {
                hidData[0] = ((but_vol_d << HID_CONTROL_VOLDN_SHIFT) | (but_vol_u << HID_CONTROL_VOLUP_SHIFT));
                state = STATE_HOLD;
            }
            state_counter_ms++;
        }
    }

    else //Nothing pressed
    {
        if (but_last != but_now)    // Has button been newly released?
        {
            state++;
            state_counter_ms = 0;
        }
        else                        // Has been released for a while
        {
            if (state_counter_ms == RELEASED_THRESHOLD_16MS) // Has been released for long enough to count as single tap
            {
                if (state == STATE_FIRST_RELEASE)
                {
                    extract_buttons(but_current, but_vol_d, but_pp, but_vol_u);
                    hidData[0] = ((but_vol_d << HID_CONTROL_VOLDN_SHIFT) | (but_vol_u << HID_CONTROL_VOLUP_SHIFT) | (but_pp << HID_CONTROL_PLAYPAUSE_SHIFT));
                    state = STATE_IDLE;
                }
                if (state >= STATE_SECOND_RELEASE)
                {
                    state = STATE_IDLE;
                }
            }
            else
            {
            }
            state_counter_ms++;
        }
    }
    but_last = but_now;
}

#endif
