#include <xccompat.h>
#include <stdint.h>
#include <stdio.h>
#define DEBUG_PRINT_ENABLE  1
#include "debug_print.h"
#include "devicedefines.h"
#include "xud.h"
#include "usb_std_requests.h"
#include "usb_device.h"
#include "hid.h"
#include "control.h"
#include "vendorrequests.h"

#define EP0_MAX_PACKET_SIZE     64

int VendorRequests(XUD_ep ep0_out, XUD_ep ep0_in, REFERENCE_PARAM(USB_SetupPacket_t, sp) VENDOR_REQUESTS_PARAMS_DEC_)
{
    XUD_Result_t result = XUD_RES_ERR;
    unsigned char request_data[EP0_MAX_PACKET_SIZE];
    unsigned request_data_length = 0;
    unsigned direction = sp.bmRequestType.Direction;

    debug_printf("Vendor request direction=%d\n", direction);
    switch (direction)
    {
        case USB_BM_REQTYPE_DIRECTION_H2D: //0 = SET
            request_data_length = 0; /* length not required by XUD API coming in */
            result = XUD_GetBuffer(ep0_out, request_data, request_data_length);
            if (result == XUD_RES_OKAY) 
            {
                 control_process_usb_set_request(sp.wIndex, sp.wValue, request_data_length, request_data, i_control, 1);
                 result = XUD_DoSetRequestStatus(ep0_in);
            }
            break;

        case USB_BM_REQTYPE_DIRECTION_D2H: //1 = GET
            /* application retrieval latency inside the control library call
                 * XUD task defers further calls by NAKing USB transactions
                 */
            size_t len;
            control_process_usb_get_request(sp.wIndex, sp.wValue, len, request_data, i_control, 1);
            result = XUD_DoGetRequest(ep0_out, ep0_in, request_data, len, sp.wLength);
            break;

        default:
            __builtin_unreachable();
            break;
    }
    return result;
}


