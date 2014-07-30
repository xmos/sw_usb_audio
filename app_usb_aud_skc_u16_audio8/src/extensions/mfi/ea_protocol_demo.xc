#ifdef IAP

#include "iap.h"

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

#endif
