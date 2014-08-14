#ifdef IAP_EA_NATIVE_TRANS

#include "iap.h"

#define DEBUG_UNIT EA_PROTOCOL_DEMO_DEBUG
#include "debug_print.h"

#define COM_XMOS_DEMO_PROTOCOL_VERSION 0x01

/*
 * com.xmos.demo protocol message layout:
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

#define MIN_VALID_MSG_LEN     (MESSAGE_TYPE_OFFSET + MESSAGE_TYPE_SIZE) // Smallest valid message must contain length and type bytes

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

int com_xmos_demo_led_ctrl_command_parser(unsigned char message[n], unsigned n)
{
    com_xmos_demo_led_ctrl_commands_t demo_command = message[DEMO_CMD_OFFSET];
    switch (demo_command)
    {
        case LED_OFF_CMD:
            //TODO: LED off
            debug_printf("EA Protocol demo: LED_OFF_CMD received\n");
            return 0;
        case LED_ON_CMD:
            //TODO: LED on
            debug_printf("EA Protocol demo: LED_ON_CMD received\n");
            return 0;
    }
    return 1;
}

int com_xmos_demo_protocol_message_parser(unsigned char packet_data[n], unsigned n)
{
    if (n < MIN_VALID_MSG_LEN)
    {
        // Do not attempt to parse a packet shorter than the minimum valid length
        debug_printf("EA Protocol demo: ERROR - Packet data of %d bytes shorter than the minimum valid length of %d for a message\n", n, MIN_VALID_MSG_LEN);
        return n;
    }

    // Get the length of the first message the packet data
    short message_length = ((packet_data[MESSAGE_LENGTH_OFFSET] << 8) | packet_data[MESSAGE_LENGTH_OFFSET+1]);

    if (message_length < MIN_VALID_MSG_LEN)
    {
        // Message is shorter than minimum expected length
        debug_printf("EA Protocol demo: ERROR - Message length of %d shorter than the minimum valid length of %d\n", message_length, MIN_VALID_MSG_LEN);
        return message_length;
    }
    if (n < message_length)
    {
        // Message exceeds length of packet data
        debug_printf("EA Protocol demo: ERROR - Message length of %d exceeds length of packet data %d bytes\n", message_length, n);
        return message_length;
    }

    // Parse message
    com_xmos_demo_protocol_msg_t message_type = packet_data[MESSAGE_TYPE_OFFSET];
    short message_data_length = (message_length - MESSAGE_DATA_OFFSET);

    debug_printf("EA Protocol demo: packet of length %d received, %d bytes of message data\n", message_length, message_data_length);

    // Check protocol message type
    switch (message_type)
    {
        case STOP_CMD:
            debug_printf("EA Protocol demo: STOP_CMD received\n");
            //TODO: reset any state
            // Do not ACK
            return message_length;
        case START_CMD:
            debug_printf("EA Protocol demo: START_CMD received\n");
            // Check we're using the same protocol version as the iOS app
            if (message_data_length == 1)
            {
                char iOS_protocol_version = packet_data[MESSAGE_DATA_OFFSET];
                if (iOS_protocol_version == COM_XMOS_DEMO_PROTOCOL_VERSION)
                {
                    // We can proceed as we're both using the same version
                    //TODO: Send ACK
                    return message_length;
                }
                else
                {
                    debug_printf("EA Protocol demo: ERROR - Incompatible protocol versions:\nxCORE firmware using version %d\niOS app using version %d\n", COM_XMOS_DEMO_PROTOCOL_VERSION, iOS_protocol_version);
                }
            }
            break;
        case ACK_CMD:
            debug_printf("EA Protocol demo: ACK_CMD received\n");
            //TODO: update any required state
            return message_length;
        case NACK_CMD:
            debug_printf("EA Protocol demo: NACK_CMD received\n");
            //TODO: update any required state
            return message_length;
        case SUPPORTED_DEMO_COMMAND_SETS_CMD:
            debug_printf("EA Protocol demo: SUPPORTED_DEMO_COMMAND_SETS_CMD received\n");
            /* Don't currently need to do anything with this information,
             * printing out all supported command sets for debug purposes
             */
            debug_printf("EA Protocol demo: iOS app supports the following demo command sets:\n");
            for (int i = 0; i < message_data_length; i++)
            {
                debug_printf("EA Protocol demo: 0x%x\n", packet_data[MESSAGE_DATA_OFFSET+i]);
            }
            //TODO: send ACK
            //TODO: send our supported demo command sets
            return message_length;
        case DEMO_CMD:
            debug_printf("EA Protocol demo: DEMO_CMD received...\n");
            // Check demo command from supported demo command set
            if (packet_data[MESSAGE_DATA_OFFSET] == LED_CTRL)
            {
                // Act on demo command
                if (com_xmos_demo_led_ctrl_command_parser(packet_data, message_length))
                {
                    // Problem parsing demo command
                    break;
                }
                //TODO: ACK
                return message_length;
            }
            break;
        default:
            // Unrecognised protocol message type
            debug_printf("EA Protocol demo: ERROR - Unrecognised command received\n");
            break;
    }
    //TODO: Send NACK
    return message_length;
}

void usb_packet_parser(unsigned char usb_packet[n], unsigned n)
{
    /*
     * The USB packet passed in may contain multiple protocol messages,
     * so we try to parse all of the data in the packet
     */

    // Check packet length is not zero
    if (n > 0)
    {
        int current_position = 0;
        while (current_position < n)
        {
            current_position += com_xmos_demo_protocol_message_parser(&usb_packet[current_position], (n - current_position));
        }
    }
    else
    {
        // Zero length packet
        debug_printf("EA Protocol demo: Zero length packet received\n");
    }
}

void ea_protocol_demo(chanend c_ea_data)
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
                usb_packet_parser(data, dataLength);
                break;
        }
    }
}

#endif /* IAP_EA_NATIVE_TRANS */
