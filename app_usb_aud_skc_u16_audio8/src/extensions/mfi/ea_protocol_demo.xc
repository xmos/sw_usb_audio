#ifdef IAP_EA_NATIVE_TRANS

#include "iap.h"

#define DEBUG_UNIT EA_PROTOCOL_DEMO_DEBUG
#include "debug_print.h"

#define COM_XMOS_DEMO_PROTOCOL_VERSION 0x01

/*
 * com.xmos.demo protocol packet layout:
 *
 * MESSAGE_LENGTH | MESSAGE_TYPE | MESSAGE_DATA
 *   0xNN 0xNN    |     0xNN     | 0xNN ... 0xNN
 */
#define MESSAGE_LENGTH_OFFSET 0
#define MESSAGE_LENGTH_SIZE   2 // Size in bytes
#define MESSAGE_TYPE_OFFSET   (MESSAGE_LENGTH_OFFSET + MESSAGE_LENGTH_SIZE)
#define MESSAGE_TYPE_SIZE     1 // Size in bytes
#define MESSAGE_DATA_OFFSET   (MESSAGE_TYPE_OFFSET + MESSAGE_TYPE_SIZE)
#define DEMO_CMD_OFFSET       (MESSAGE_DATA_OFFSET + 1)

typedef enum com_xmos_demo_protocol_msg_t
{
    STOP_CMD,
    START_CMD,
    ACK_CMD,
    NACK_CMD,
    SUPPORTED_DEMO_COMMAND_SETS_CMD,
    DEMO_CMD,
} com_xmos_demo_protocol_msg_t;

typedef enum com_xmos_demo_command_sets_t
{
    LED_CTRL,
    NUM_DEMO_COMMAND_SETS, // <- End marker
} com_xmos_demo_command_sets_t;

typedef enum com_xmos_demo_led_ctrl_commands_t
{
    LED_OFF_CMD,
    LED_ON_CMD,
} com_xmos_demo_led_ctrl_commands_t;

int com_xmos_demo_led_ctrl_command_parser(unsigned char packet[n], unsigned n)
{
    com_xmos_demo_led_ctrl_commands_t demo_command = packet[DEMO_CMD_OFFSET];
    switch (demo_command)
    {
        case LED_OFF_CMD:
            //TODO: LED off
            return 0;
        case LED_ON_CMD:
            //TODO: LED on
            return 0;
    }
    return 1;
}

void com_xmos_demo_protocol_message_parser(unsigned char packet[n], unsigned n)
{
    // Check packet length is not zero
    if (n > 0)
    {
        short message_length = (packet[MESSAGE_LENGTH_OFFSET] | (packet[MESSAGE_LENGTH_OFFSET + 1] << 8)) - MESSAGE_LENGTH_SIZE;
        if (message_length > 0)
        {
            com_xmos_demo_protocol_msg_t message_type = packet[MESSAGE_TYPE_OFFSET];
            short message_data_lenght = (message_length - MESSAGE_DATA_OFFSET);

            // Check protocol message type
            switch (message_type)
            {
                case STOP_CMD:
                    debug_printf("EA Protocol demo: STOP_CMD received\n");
                    //TODO: reset any state
                    // Do not ACK
                    return;
                case START_CMD:
                    debug_printf("EA Protocol demo: START_CMD received\n");
                    // Check we're using the same protocol version as the iOS app
                    if (message_data_lenght == 1)
                    {
                        char iOS_protocol_version = packet[MESSAGE_DATA_OFFSET];
                        if (iOS_protocol_version == COM_XMOS_DEMO_PROTOCOL_VERSION)
                        {
                            // We can proceed as we're both using the same version
                            //TODO: Send ACK
                            return;
                        }
                        else
                        {
                            debug_printf("EA Protocol demo: Incompatible protocol versions:\nxCORE firmware using version %d\niOS app using version %d\n", COM_XMOS_DEMO_PROTOCOL_VERSION, iOS_protocol_version);
                        }
                    }
                    break;
                case ACK_CMD:
                    debug_printf("EA Protocol demo: ACK_CMD received\n");
                    //TODO: update any required state
                    return;
                case NACK_CMD:
                    debug_printf("EA Protocol demo: NACK_CMD received\n");
                    //TODO: update any required state
                    return;
                case SUPPORTED_DEMO_COMMAND_SETS_CMD:
                    debug_printf("EA Protocol demo: SUPPORTED_DEMO_COMMAND_SETS_CMD received\n");
                    /* Don't currently need to do anything with this information,
                     * printing out all supported command sets for debug purposes
                     */
                    debug_printf("EA Protocol demo: iOS app supports the following demo command sets:\n");
                    for (int i = 0; i < message_data_lenght; i++)
                    {
                        debug_printf("EA Protocol demo: 0x%x\n", packet[MESSAGE_DATA_OFFSET+i]);
                    }
                    //TODO: send ACK
                    //TODO: send our supported demo command sets
                    return;
                case DEMO_CMD:
                    debug_printf("EA Protocol demo: DEMO_CMD received\n");
                    // Check demo command from supported demo command set
                    if (packet[MESSAGE_DATA_OFFSET] == LED_CTRL)
                    {
                        // Act on demo command
                        if (com_xmos_demo_led_ctrl_command_parser(packet, n))
                        {
                            // Problem parsing demo command
                            break;
                        }
                        //TODO: ACK
                        return;
                    }
                    break;
                default:
                    // Unrecognised protocol message type
                    debug_printf("EA Protocol demo: Unrecognised command received\n");
                    break;
            }
        }
        else
        {
            // Zero length message
            debug_printf("EA Protocol demo: Zero length message received\n");
        }
    }
    else
    {
        // Zero length packet
        debug_printf("EA Protocol demo: Zero length packet received\n");
    }
    //TODO: Send NACK
}

void ea_protocol_demo(chanend c_ea_data)
{
    while (1)
    {
        char data[IAP2_EA_NATIVE_TRANS_MAX_PACKET_SIZE];

        select
        {
            case c_ea_data :> int dataLength:
                // Receive the data
                for (int i = 0; i < dataLength; i++)
                {
                    c_ea_data :> data[i];
                }
                break;
        }
    }
}

#endif /* IAP_EA_NATIVE_TRANS */
