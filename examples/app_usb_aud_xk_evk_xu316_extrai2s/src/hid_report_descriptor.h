// Copyright 2021 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#ifndef __hid_report_descriptor_h__
#define __hid_report_descriptor_h__

#include "xua_hid_report_descriptor.h"

#if 0
/* Existing static report descriptor kept for reference */
unsigned char hidReportDescriptor[] =
{
    0x05, 0x0c,     /* Usage Page (Consumer Device) */
    0x09, 0x01,     /* Usage (Consumer Control) */
    0xa1, 0x01,     /* Collection (Application) */
    0x15, 0x00,     /* Logical Minimum (0) */
    0x25, 0x01,     /* Logical Maximum (1) */
    0x09, 0xb0,     /* Usage (Play) */
    0x09, 0xb5,     /* Usage (Scan Next Track) */
    0x09, 0xb6,     /* Usage (Scan Previous Track) */
    0x09, 0xe9,     /* Usage (Volume Up) */
    0x09, 0xea,     /* Usage (Volume Down) */
    0x09, 0xe2,     /* Usage (Mute) */
    0x75, 0x01,     /* Report Size (1) */
    0x95, 0x06,     /* Report Count (6) */
    0x81, 0x02,     /* Input (Data, Var, Abs) */
    0x95, 0x02,     /* Report Count (2) */
    0x81, 0x01,     /* Input (Cnst, Ary, Abs) */
    0xc0            /* End collection */
};
#endif

/*
 * Define non-configurable items in the HID Report descriptor.
 */
static const USB_HID_Short_Item_t hidCollectionApplication  = { .header = 0xA1, .data = { 0x01, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidCollectionEnd          = { .header = 0xC0, .data = { 0x00, 0x00 }, .location = 0x00 };

static const USB_HID_Short_Item_t hidInputConstArray        = { .header = 0x81, .data = { 0x01, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidInputDataVar           = { .header = 0x81, .data = { 0x02, 0x00 }, .location = 0x00 };

static const USB_HID_Short_Item_t hidLogicalMaximum0        = { .header = 0x25, .data = { 0x00, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidLogicalMaximum1        = { .header = 0x25, .data = { 0x01, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidLogicalMinimum0        = { .header = 0x15, .data = { 0x00, 0x00 }, .location = 0x00 };

static const USB_HID_Short_Item_t hidReportCount2           = { .header = 0x95, .data = { 0x02, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidReportCount6           = { .header = 0x95, .data = { 0x06, 0x00 }, .location = 0x00 };
static const USB_HID_Short_Item_t hidReportSize1            = { .header = 0x75, .data = { 0x01, 0x00 }, .location = 0x00 };

static const USB_HID_Short_Item_t hidUsageConsumerControl   = { .header = 0x09, .data = { 0x01, 0x00 }, .location = 0x00 };

static const USB_HID_Short_Item_t hidUsagePageConsumer      = { .header = 0x05, .data = { 0x0C, 0x00 }, .location = 0x00 };

/*
 * Define configurable items in the HID Report descriptor.
 */
static USB_HID_Short_Item_t hidUsageByte0Bit5   = { .header = 0x09, .data = { 0xE2, 0x00 }, .location = 0x50 }; // Mute
static USB_HID_Short_Item_t hidUsageByte0Bit4   = { .header = 0x09, .data = { 0xEA, 0x00 }, .location = 0x40 }; // Vol-
static USB_HID_Short_Item_t hidUsageByte0Bit3   = { .header = 0x09, .data = { 0xE9, 0x00 }, .location = 0x30 }; // Vol+
static USB_HID_Short_Item_t hidUsageByte0Bit2   = { .header = 0x09, .data = { 0xB6, 0x00 }, .location = 0x20 }; // Scan Prev
static USB_HID_Short_Item_t hidUsageByte0Bit1   = { .header = 0x09, .data = { 0xB5, 0x00 }, .location = 0x10 }; // Scan Next
static USB_HID_Short_Item_t hidUsageByte0Bit0   = { .header = 0x09, .data = { 0xB0, 0x00 }, .location = 0x00 }; // Play

/*
 * List the configurable items in the HID Report descriptor.
 */
static USB_HID_Short_Item_t* const hidConfigurableItems[] = {
    &hidUsageByte0Bit0,
    &hidUsageByte0Bit1,
    &hidUsageByte0Bit2,
    &hidUsageByte0Bit3,
    &hidUsageByte0Bit4,
    &hidUsageByte0Bit5
};

/*
 * List Usage pages in the HID Report descriptor, one per byte.
 */
static const USB_HID_Short_Item_t* const hidUsagePages[] = {
    &hidUsagePageConsumer
};

/*
 * List all items in the HID Report descriptor.
 */
static const USB_HID_Short_Item_t* const hidReportDescriptorItems[] = {
    &hidUsagePageConsumer,
    &hidUsageConsumerControl,
    &hidCollectionApplication,
        &hidLogicalMinimum0,
        &hidLogicalMaximum1,
        &hidUsageByte0Bit0,
        &hidUsageByte0Bit1,
        &hidUsageByte0Bit2,
        &hidUsageByte0Bit3,
        &hidUsageByte0Bit4,
        &hidUsageByte0Bit5,
        &hidReportSize1,
        &hidReportCount6,
        &hidInputDataVar,
        &hidLogicalMaximum0,
        &hidReportCount2,
        &hidInputConstArray,
    &hidCollectionEnd
};

/*
 * Define the length of the HID Report.
 * This value must match the number of Report bytes defined by hidReportDescriptorItems.
 */
#define HID_REPORT_LENGTH   ( 1 )

#endif // __hid_report_descriptor_h__
