// Copyright (c) 2016, XMOS Ltd, All rights reserved
#include <xs1.h>
#include "xud.h"

void XUD_ClearStallByAddr(int epNum)
{
}

XUD_Result_t XUD_DoGetRequest(XUD_ep ep_out, XUD_ep ep_in,  unsigned char buffer[], unsigned length, unsigned requested)
{
  return XUD_RES_OKAY;
}

XUD_Result_t XUD_DoSetRequestStatus(XUD_ep ep_in)
{
  return XUD_RES_OKAY;
}

XUD_Result_t XUD_GetBuffer(XUD_ep ep_out, unsigned char buffer[], REFERENCE_PARAM(unsigned, length))
{
  return XUD_RES_OKAY;
}

void XUD_GetData_Select(chanend c, XUD_ep ep, REFERENCE_PARAM(unsigned, length), REFERENCE_PARAM(XUD_Result_t, result))
{
}

XUD_Result_t XUD_GetSetupBuffer(XUD_ep ep_out, unsigned char buffer[], REFERENCE_PARAM(unsigned, length))
{
  return XUD_RES_OKAY;
}

void XUD_ResetEpStateByAddr(unsigned epNum)
{
}

void XUD_SetData_Select(chanend c, XUD_ep ep, REFERENCE_PARAM(XUD_Result_t, result))
{
}

XUD_Result_t XUD_SetDevAddr(unsigned addr)
{
  return XUD_RES_OKAY;
}

void XUD_SetStallByAddr(int epNum)
{
}

void XUD_SetStall(XUD_ep ep)
{
}

void XUD_SetTestMode(XUD_ep ep, unsigned testMode)
{
}

XUD_ep XUD_InitEp(chanend c_ep)
{
  return 0;
}

XUD_BusSpeed_t XUD_ResetEndpoint(XUD_ep one, NULLABLE_REFERENCE_PARAM(XUD_ep, two))
{
  return XUD_RES_OKAY;
}

extern XUD_Result_t XUD_SetReady_InPtr(XUD_ep ep, unsigned addr, int len);
extern int XUD_SetReady_OutPtr(XUD_ep ep, unsigned addr);

int XUD_Manager(chanend c_epOut[], int noEpOut,
                chanend c_epIn[], int noEpIn,
                NULLABLE_RESOURCE(chanend, c_sof),
                XUD_EpType epTypeTableOut[], XUD_EpType epTypeTableIn[],
                NULLABLE_RESOURCE(out port, p_usb_rst),
                NULLABLE_RESOURCE(clock, clk),
                unsigned rstMask,
                XUD_BusSpeed_t desiredSpeed,
                XUD_PwrConfig pwrConfig)
{
  return 0;
}
