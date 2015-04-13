#ifdef IAP_EA_NATIVE_TRANS

#include "iap.h"
#include "ea_protocol_demo.h"
#include "com_xmos_demo.h"
#include <platform.h>
#include <timer.h>
#include <print.h>

#define BUTTONS_MASK 0xE

#define LEDS_PORTVAL_OFF 0x00
#define LEDS_PORTVAL_ON  0xFF

/* Buttons/switch port */
in port p_sw = on tile[1] : XS1_PORT_4B;

/* LED grid port */
out port p_leds_row = on tile[1] : XS1_PORT_4C;
out port p_leds_col = on tile[1] : XS1_PORT_4D;

void OutputLedVal(unsigned char x)
{
    p_leds_row <: (unsigned) (x & 0xf);
    p_leds_col <: (unsigned) (x >> 4);
}

void com_xmos_demo_led_ctrl_user(com_xmos_demo_led_ctrl_commands_t demo_command)
{
    if (demo_command == LED_OFF_CMD)
    {
        OutputLedVal(LEDS_PORTVAL_OFF);
    }
    else
    {
        OutputLedVal(LEDS_PORTVAL_ON);
    }
}
//::

void ea_protocol_demo(chanend c_ea_data)
{
    unsigned char current_val = 0xFF; // Buttons pulled up
    int is_stable = 1;
    timer tmr;
    const unsigned debounce_delay_ms = 50;
    unsigned debounce_timeout;
    unsigned char ledVals = LEDS_PORTVAL_OFF;

    OutputLedVal(ledVals);

    ea_demo_init();

    while (1)
    {
        char data[IAP2_EA_NATIVE_TRANS_MAX_PACKET_SIZE];
        unsigned dataLength;
        int ea_control;

        select
        {
            case iAP2_EANativeTransport_readFromChan(c_ea_data, ea_control, data, dataLength):
                if (ea_control == EA_NATIVE_SEND_CONTROL)
                {
                    switch (data[0])
                    {
                        case EA_NATIVE_RESET:
                        case EA_NATIVE_DISCONNECTED:
                            // Disable the LED mask as the EA Protocol demo is no longer active
                            OutputLedVal(LEDS_PORTVAL_OFF);
                            ea_demo_init(); // Clear any queued but unsent data
                            break;
                        case EA_NATIVE_CONNECTED:
                            // Start with the LED off
                            OutputLedVal(LEDS_PORTVAL_OFF);
                            break;
                        case EA_NATIVE_DATA_SENT:
                            ea_demo_data_sent();
                            // Can now send more data if required
                            ea_demo_dispatch_data(c_ea_data);
                            break;
                    }
                }
                else
                {
                    ea_demo_usb_packet_parser(data, dataLength, c_ea_data);
                }
                break;
                //::

            /* Button handler */
            // If the button is "stable", react when the I/O pin changes value
            case is_stable => p_sw when pinsneq(current_val) :> current_val:

                /* Check if button 1 is pressed */
                if ((current_val | BUTTONS_MASK) == BUTTONS_MASK)
                {
                    /* LED used for EA Protocol demo is on when the mask is disabled */
                    if (ledVals == LEDS_PORTVAL_ON)
                    {
                        /* So turn it off now
                         * and send protocol message so this change of state is reflect correctly
                         */
                        ledVals = LEDS_PORTVAL_OFF;
                        ea_demo_process_user_input(0, c_ea_data);
                    }
                    else
                    {
                        /* So turn it on now
                         * and send protocol message so this change of state is reflect correctly
                         */
                        ledVals = LEDS_PORTVAL_ON;
                        ea_demo_process_user_input(1, c_ea_data);
                    }
                }

                is_stable = 0;
                unsigned current_time;
                tmr :> current_time;
                // Calculate time to event after debounce period
                debounce_timeout = current_time + (debounce_delay_ms * (XS1_TIMER_HZ/1000));
                break;

            /* If the button is not stable (i.e. bouncing around) then select
             * when we the timer reaches the timeout to renter a stable period
             */
            case !is_stable => tmr when timerafter(debounce_timeout) :> void:
                is_stable = 1;
                break;
            //::
        }
    }
}

#endif /* IAP_EA_NATIVE_TRANS */
