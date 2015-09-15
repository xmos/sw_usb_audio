
#include <xs1.h>
#include <platform.h>

#include "devicedefines.h"

#ifdef HID_CONTROLS
in port p_sw = on tile[1] : XS1_PORT_4B;

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
 * 4: Volime Down
 * 5: Mute
 */

unsigned multicontrol_count = 0;
unsigned wait_counter =0;


#define THRESH 1
#define MULTIPRESS_WAIT 25

#define HID_CONTROL_NEXT 		0x02
#define HID_CONTROL_PLAYPAUSE 	0x01
#define HID_CONTROL_PREV		0x04
#define HID_CONTROL VOLUP       0x08
#define HID_CONTROL_VOLDN		0x10
#define HID_CONTROL_MUTE		0x20

typedef enum
{
	STATE_IDLE = 0x00,
	STATE_PLAY = 0x01,
	STATE_NEXTPREV = 0x02,
}t_controlState;

t_controlState state;

unsigned lastA;

void UserReadHIDButtons(unsigned char hidData[])
{
    /* Variables for buttons a, b, c and switch sw */
    unsigned a, b, c, sw, tmp;

    p_sw :> tmp;

    /* Buttons are active low */
    tmp = ~tmp;

    a = (tmp & (P_GPI_BUTA_MASK))>>P_GPI_BUTA_SHIFT;
    b = (tmp & (P_GPI_BUTB_MASK))>>P_GPI_BUTB_SHIFT;
    c = (tmp & (P_GPI_BUTC_MASK))>>P_GPI_BUTC_SHIFT;
    sw = (tmp & (P_GPI_SW1_MASK))>>P_GPI_SW1_SHIFT;

    if(sw)
    {
        /* Assign buttons A and B to Vol Up/Down */
        hidData[0] = (a << 4) | (b << 3) | (c << 5);
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

    	    if(wait_counter > MULTIPRESS_WAIT)
            {
    		    if(state == STATE_PLAY)
                {
    			    hidData[0] = HID_CONTROL_PLAYPAUSE;
    		    }
    		    else if(state == STATE_NEXTPREV)
                {
                    if(lastA)
    			        hidData[0] = HID_CONTROL_PREV;
    		        else
    			        hidData[0] = HID_CONTROL_NEXT;
                }
    		    state = STATE_IDLE;
    	    }
    	    multicontrol_count = 0;
        }
    }
}

#endif
