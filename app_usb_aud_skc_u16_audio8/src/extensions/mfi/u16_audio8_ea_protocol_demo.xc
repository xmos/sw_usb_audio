#ifdef IAP_EA_NATIVE_TRANS

#include "iap.h"
#include "ea_protocol_demo.h"
#include "gpio.h"

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

void u16_audio8_ea_protocol_demo(chanend c_ea_data)
{
    while (1)
    {
        char data[IAP2_EA_NATIVE_TRANS_MAX_PACKET_SIZE];

        select //TODO: could use iAP2_EANativeTransport_dataToiOS() here - would need to update names etc. to keep it clear
        {
            case c_ea_data :> int dataLength:
                // Receive the data
                for (int i = 0; i < dataLength; i++)
                {
                    c_ea_data :> data[i];
                }
                usb_packet_parser(data, dataLength, c_ea_data);
                break;

            //TODO: Add button handler
        }
    }
}

#endif /* IAP_EA_NATIVE_TRANS */
