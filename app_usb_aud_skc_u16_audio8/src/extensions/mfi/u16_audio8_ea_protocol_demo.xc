#ifdef IAP_EA_NATIVE_TRANS

#include "iap.h"
#include "ea_protocol_demo.h"
#include "com_xmos_demo.h"
#include "gpio.h"
#include <platform.h>
#include <timer.h>

#define AUDIO8_BUTTON_1 0xE

on tile[AUDIO_IO_TILE]: in port p_buttons = PORT_BUTTON_GPIO;

void com_xmos_demo_led_ctrl_user(com_xmos_demo_led_ctrl_commands_t demo_command)
{
    if (demo_command == LED_OFF_CMD)
    {
        set_led_array_mask(LED_MASK_COL_OFF);
    }
    else
    {
        set_led_array_mask(LED_MASK_DISABLE);
    }
}
//::

void u16_audio8_ea_protocol_demo(chanend c_ea_data)
{
    unsigned char current_val = 0xFF; // Buttons pulled up
    int is_stable = 1;
    timer tmr;
    const unsigned debounce_delay_ms = 50;
    unsigned debounce_timeout;

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
                            set_led_array_mask(LED_MASK_DISABLE);
                            ea_demo_init(); // Clear any queued but unsent data
                            break;
                        case EA_NATIVE_CONNECTED:
                            // Start with the LED off
                            set_led_array_mask(LED_MASK_COL_OFF);
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
            case is_stable => p_buttons when pinsneq(current_val) :> current_val:
                if ((current_val | AUDIO8_BUTTON_1) == AUDIO8_BUTTON_1)
                {
                    // LED used for EA Protocol demo is on when the mask is disabled
                    if (get_led_array_mask() == LED_MASK_DISABLE)
                    {
                        /* So turn it off now
                         * and send protocol message so this change of state is reflect correctly
                         */
                        ea_demo_process_user_input(0, c_ea_data);
                    }
                    else
                    {
                        /* So turn it on now
                         * and send protocol message so this change of state is reflect correctly
                         */
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
