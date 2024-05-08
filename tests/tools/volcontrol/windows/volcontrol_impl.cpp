#include "volcontrol_impl.h"
#include "volcontrol.h"

#include <cmath>


/* A.14 Audio Class-Specific Request Codes */
#define REQUEST_CODE_UNDEFINED      0x00
#define CUR   (1)
#define RANGE (2)
#define MEM   (3)

/* A.17 Control Selector Codes */
/* A.17.1 Clock Source Control Selectors */
#define CS_CONTROL_UNDEFINED        0x00
#define CS_SAM_FREQ_CONTROL         0x01
#define CS_CLOCK_VALID_CONTROL      0x02

/* A.17.2 Clock Selector Control Selectors */
#define CX_CONTROL_UNDEFINED        0x00
#define CX_CLOCK_SELECTOR_CONTROL   0x01

/* Clock unit IDs */
#define ID_CLKSEL                40              /* Clock selector ID */
#define ID_CLKSRC_INT            41              /* Clock source ID (internal) */
#define ID_CLKSRC_SPDIF          42              /* Clock source ID (external) */
#define ID_CLKSRC_ADAT           43              /* Clock source ID (external) */


TUsbAudioApiDll gDrvApi;


/* Issue a generic control/class GET request to a specific unit in the Audio Interface */
int usb_audio_class_get(TUsbAudioHandle h, unsigned char bRequest, unsigned char cs, unsigned char cn, unsigned char unitID, unsigned int wLength, unsigned char* data)
{
    return gDrvApi.TUSBAUDIO_AudioControlRequestGet(h,
        unitID,
        bRequest,
        cs,
        cn,
        data,
        wLength,
        NULL,
        1000);
}

/* Issue a generic control/class SET request to a specific unit in the Audio Interface */
int usb_audio_class_set(TUsbAudioHandle h, unsigned char bRequest, unsigned char cs, unsigned char cn, unsigned char unitID, unsigned short wLength, unsigned char* data)
{
    return gDrvApi.TUSBAUDIO_AudioControlRequestSet(h,
        unitID,
        bRequest,
        cs,
        cn,
        data,
        wLength,
        NULL,
        1000);
}

int usb_audio_set_clock(TUsbAudioHandle h, unsigned clkSrcId)
{
    return gDrvApi.TUSBAUDIO_SetCurrentClockSource(h, clkSrcId);
}

int usb_audio_request_set(AudioDeviceHandle h, unsigned char bRequest, unsigned char cs,
    unsigned char cn, unsigned char unitId,
    unsigned char* data, unsigned short datalength)
{
    char reqStr[] = "Custom";

    if (bRequest == CUR)
    {
        strcpy(reqStr, "CUR");
    }
    else if (bRequest == RANGE)
    {
        strcpy(reqStr, "RANGE");
    }
    else
    {
        strcpy(reqStr, "MEM");
    }

    return usb_audio_class_set(h, bRequest, cs, cn, unitId, datalength, data);
}


int usb_audio_request_get(AudioDeviceHandle h, unsigned char bRequest, unsigned char cs, unsigned char cn, unsigned char unitId, unsigned char* data)
{
    char reqStr[] = "Custom";

    if (bRequest == CUR)
    {
        strcpy(reqStr, "CUR");
    }
    else if (bRequest == RANGE)
    {
        strcpy(reqStr, "RANGE");
    }
    else if (bRequest == MEM)
    {
        strcpy(reqStr, "MEM");
    }

    return usb_audio_class_get(h, bRequest, cs, cn, unitId, 64, data);
}


float getVolume(AudioDeviceHandle deviceID, uint32_t scope, uint32_t channel) {
    unsigned char bRequest = CUR;
    unsigned char cs = 2;
    unsigned char cn = channel;
    unsigned char unitId = scope == ScopeOutput ? 10 : 11;
    int datalength = 0;
    unsigned char data[64];
    datalength = usb_audio_request_get(deviceID, bRequest, cs, cn, unitId, data);
    if (data[0] == 0 && data[1] == 0x81)
        return 0;

    if (data[0] == 0 && data[1] == 0)
        return 1;

    char msb = data[1];
    char lsb = data[0];
    float val = (float)(128 + msb) + (float)lsb / 256;

    return val / 128;
}



void setVolume(AudioDeviceHandle deviceID, uint32_t scope, uint32_t channel,
    float volume)
{
    unsigned char bRequest = CUR;
    unsigned char cs = 2;
    unsigned char cn = channel;
    unsigned char unitId = scope == ScopeOutput ? 10 : 11;
    unsigned char data[64];
    if (volume == 0) {
        data[0] = 0;
        data[1] = 0x81;
    }
    else if (volume == 1) {
        data[0] = data[1] = 0;
    }
    else {
        float frac;
        volume *= 128.;
        volume = volume - 128;
        volume = volume / 2; // why?
        frac = (volume - round(volume)) * 256;
        data[0] = (char)frac;
        data[1] = (char)volume;
    }
    usb_audio_request_set(deviceID, bRequest, cs, cn, unitId, data, 2);
}

void setClock(AudioDeviceHandle deviceID, uint32_t clockId)
{
    // Check the validity of the clock
    unsigned char bRequest = CUR;
    unsigned char cs = CS_CLOCK_VALID_CONTROL;
    unsigned char cn = 0;
    unsigned char unitId = ID_CLKSEL + clockId;
    int wLength = 64;
    unsigned char data[64];
    if (0 != usb_audio_class_get(deviceID, bRequest, cs, cn, unitId, wLength, data)) {
        printf("Error: failed to get clock validity\n");
        exit(1);
    }
    if (data[0] != 1) {
        printf("Error: Clock is not valid yet\n");
        exit(1);
    }

    // Set the clock
    bRequest = CUR;
    cs = CX_CLOCK_SELECTOR_CONTROL;
    cn = 0;
    data[0] = clockId;
    wLength = 1;

    if (0 != usb_audio_set_clock(deviceID, unitId)) {
        printf("Error: failed to select clock\n");
        exit(1);
    }
}

// Maximum number of formats supported by TUSB SDK
#define MAX_FORMAT_COUNT   (32)

void setStreamFormat(AudioDeviceHandle deviceID, uint32_t scope, int sample_rate, unsigned num_chans, unsigned bit_depth)
{
    // Windows implementation doesn't set the sample rate
    (void)sample_rate;

    TUsbAudioStatus err;
    TUsbAudioStreamFormat formats[MAX_FORMAT_COUNT];
    unsigned num_formats;

    err = gDrvApi.TUSBAUDIO_GetSupportedStreamFormats(deviceID, scope == ScopeInput, MAX_FORMAT_COUNT, formats, &num_formats);
    if (0 != err) {
        printf("Error: failed to get supported stream formats, error %d\n", err);
        exit(1);
    }

    unsigned i, format_id;
    for (i = 0; i < num_formats; ++i) {
        if ((formats[i].numberOfChannels == num_chans) &&
            (formats[i].bitsPerSample == bit_depth))
        {
            format_id = formats[i].formatId;
            break;
        }
    }
    if (i == num_formats) {
        printf("Error: no format matching %u channels with %u bit resolution\n", num_chans, bit_depth);
        exit(1);
    }

    err = gDrvApi.TUSBAUDIO_SetCurrentStreamFormat(deviceID, scope == ScopeInput, format_id);
    if (0 != err) {
        printf("Error %d setting stream format\n", err);
        exit(1);
    }
}

AudioDeviceHandle getXMOSDeviceID(TCHAR guid[GUID_STR_LEN])
{
    TUsbAudioStatus st;
    TUsbAudioHandle h;

    gDrvApi.LoadByGUID(guid);

    st = gDrvApi.TUSBAUDIO_EnumerateDevices();
    if (TSTATUS_SUCCESS != st) {
        printf("Cannot enumerate devices\n");
        exit(1);
    }

    unsigned int devcnt = gDrvApi.TUSBAUDIO_GetDeviceCount();
    if (0 == devcnt) {
        printf("Cannot find any XMOS devices\n");
        exit(1);
    }
    st = gDrvApi.TUSBAUDIO_OpenDeviceByIndex(0, &h);
    if (TSTATUS_SUCCESS != st) {
        printf("Cannot open XMOS device");
        exit(1);
    }
    return h;
}

void finish(void) {
    Sleep(2000);
}
