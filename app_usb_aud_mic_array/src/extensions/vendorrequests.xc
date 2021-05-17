
#ifdef XVSM
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

void VendorRequests_Init(VENDOR_REQUESTS_PARAMS_DEC)
{
    control_init();
    control_register_resources(i_control, 1);
}

int VendorRequests(XUD_ep ep0_out, XUD_ep ep0_in, REFERENCE_PARAM(USB_SetupPacket_t, sp) VENDOR_REQUESTS_PARAMS_DEC_)
{
    XUD_Result_t result = XUD_RES_ERR;
    unsigned char request_data[EP0_MAX_PACKET_SIZE];
    size_t len;

    switch ((sp.bmRequestType.Direction << 7) | (sp.bmRequestType.Type << 5) | (sp.bmRequestType.Recipient)) 
    {

        case USB_BMREQ_H2D_VENDOR_DEV:

            result = XUD_GetBuffer(ep0_out, request_data, len);
         
            if (result == XUD_RES_OKAY) 
            {
                if (control_process_usb_set_request(sp.wIndex, sp.wValue, sp.wLength, request_data, i_control) == CONTROL_SUCCESS)
                {
                    /* zero length data to indicate success
                    * on control error, go to standard requests, which will issue STALL
                    */
                    result = XUD_DoSetRequestStatus(ep0_in);
                }
                else
                {
                    result = XUD_RES_ERR;
                }
          }
          break;

        case USB_BMREQ_D2H_VENDOR_DEV:

            /* application retrieval latency inside the control library call
            * XUD task defers further calls by NAKing USB transactions
            */
            if (control_process_usb_get_request(sp.wIndex, sp.wValue, sp.wLength, request_data, i_control) == CONTROL_SUCCESS) 
            {
                len = sp.wLength;
                result = XUD_DoGetRequest(ep0_out, ep0_in, request_data, len, len);
                /* on control error, go to standard requests, which will issue STALL */
             }
            else
            {  
                result = XUD_RES_ERR;
            }

          break;
      }

    return result;
}
#endif

