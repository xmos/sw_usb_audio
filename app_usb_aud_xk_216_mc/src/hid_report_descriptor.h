// Copyright 2022 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#ifndef _hid_report_descriptor_h_
#define _hid_report_descriptor_h_

#include "xua_hid_report.h"

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
static const USB_HID_Short_Item_t hidCollectionApplication  = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_MAIN, HID_REPORT_ITEM_TAG_COLLECTION),
    .data = { 0x01, 0x00 } };
static const USB_HID_Short_Item_t hidCollectionEnd          = {
    .header = HID_REPORT_SET_HEADER(0, HID_REPORT_ITEM_TYPE_MAIN, HID_REPORT_ITEM_TAG_END_COLLECTION),
    .data = { 0x00, 0x00 } };

static const USB_HID_Short_Item_t hidInputConstArray        = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_MAIN, HID_REPORT_ITEM_TAG_INPUT),
    .data = { 0x01, 0x00 } };
static const USB_HID_Short_Item_t hidInputDataVar           = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_MAIN, HID_REPORT_ITEM_TAG_INPUT),
    .data = { 0x02, 0x00 } };

static const USB_HID_Short_Item_t hidLogicalMaximum0        = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_LOGICAL_MAXIMUM),
    .data = { 0x00, 0x00 } };
static const USB_HID_Short_Item_t hidLogicalMaximum1        = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_LOGICAL_MAXIMUM),
    .data = { 0x01, 0x00 } };
static const USB_HID_Short_Item_t hidLogicalMinimum0        = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_LOGICAL_MINIMUM),
    .data = { 0x00, 0x00 } };

static const USB_HID_Short_Item_t hidReportCount2           = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_REPORT_COUNT),
    .data = { 0x02, 0x00 } };
static const USB_HID_Short_Item_t hidReportCount6           = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_REPORT_COUNT),
    .data = { 0x06, 0x00 } };
static const USB_HID_Short_Item_t hidReportSize1            = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_REPORT_SIZE),
    .data = { 0x01, 0x00 } };

static const USB_HID_Short_Item_t hidUsageConsumerControl   = {
    .header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
    .data = { 0x01, 0x00 } };

/*
 * Define the HID Report Descriptor Item, Usage Page, Report ID and length for each HID Report
 * For internal purposes, a report element with ID of 0 must be included if report IDs are not being used.
 */
static const USB_HID_Report_Element_t hidReportPageConsumer = {
    .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_GLOBAL, HID_REPORT_ITEM_TAG_USAGE_PAGE),
    .item.data = { USB_HID_USAGE_PAGE_ID_CONSUMER, 0x00 },
    .location = HID_REPORT_SET_LOC( 0, 1, 0, 0 )
};

/*
 * Define configurable items in the HID Report descriptor.
 */
static USB_HID_Report_Element_t hidUsageByte0Bit5   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xE2, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 5)
}; // Mute
static USB_HID_Report_Element_t hidUsageByte0Bit4   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xEA, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 4)
}; // Vol-
static USB_HID_Report_Element_t hidUsageByte0Bit3   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xE9, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 3)
}; // Vol+
static USB_HID_Report_Element_t hidUsageByte0Bit2   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xB6, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 2)
}; // Scan Prev
static USB_HID_Report_Element_t hidUsageByte0Bit1   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xB5, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 1)
}; // Scan Next
static USB_HID_Report_Element_t hidUsageByte0Bit0   = {
     .item.header = HID_REPORT_SET_HEADER(1, HID_REPORT_ITEM_TYPE_LOCAL, HID_REPORT_ITEM_TAG_USAGE),
     .item.data = { 0xB0, 0x00 },
     .location = HID_REPORT_SET_LOC(0, 0, 0, 0)
}; // Play

/*
 * List the configurable elements in the HID Report descriptor.
 */
static USB_HID_Report_Element_t* const hidConfigurableElements[] = {
    &hidUsageByte0Bit0,
    &hidUsageByte0Bit1,
    &hidUsageByte0Bit2,
    &hidUsageByte0Bit3,
    &hidUsageByte0Bit4,
    &hidUsageByte0Bit5
};

/*
 * List HID Reports, one per Report ID.
 * If not using report IDs - still have one with report ID 0
 */
static const USB_HID_Report_Element_t* const hidReports[] = {
    &hidReportPageConsumer
};

/*
 * List all items in the HID Report descriptor.
 */
static const USB_HID_Short_Item_t* const hidReportDescriptorItems[] = {
    &(hidReportPageConsumer.item),
    &hidUsageConsumerControl,
    &hidCollectionApplication,
        &hidLogicalMinimum0,
        &hidLogicalMaximum1,
        &(hidUsageByte0Bit0.item),
        &(hidUsageByte0Bit1.item),
        &(hidUsageByte0Bit2.item),
        &(hidUsageByte0Bit3.item),
        &(hidUsageByte0Bit4.item),
        &(hidUsageByte0Bit5.item),
        &hidReportSize1,
        &hidReportCount6,
        &hidInputDataVar,
        &hidLogicalMaximum0,
        &hidReportCount2,
        &hidInputConstArray,
    &hidCollectionEnd
};

/*
 * Define the number of HID Reports
 * Due to XC not supporting designated initializers, this constant has a hard-coded value.
 * It must equal ( sizeof hidReports / sizeof ( USB_HID_Report_Element_t* ))
 */
#define HID_REPORT_COUNT ( 1 )

#endif // _hid_report_descriptor_h_
