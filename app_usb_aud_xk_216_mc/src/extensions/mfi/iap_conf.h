#define IAP1 1
#define IAP2 1

/* Include global device configuration defines */
#include "xua.h"
#include "descriptor_defs.h"

/***** Defines relating to iOS identification *****/
#define ACCESSORY_MODEL_NUMBER   "xCORE-200 MC AUDIO"

#define ACCESSORY_HARDWARE_MAJOR 2
#define ACCESSORY_HARDWARE_MINOR 0
#define ACCESSORY_HARDWARE_POINT 0

/* By default base the iAP version number on USB BCD_DEVICE */
#define ACCESSORY_FIRMWARE_MAJOR BCD_DEVICE_J
#define ACCESSORY_FIRMWARE_MINOR BCD_DEVICE_M
#define ACCESSORY_FIRMWARE_POINT BCD_DEVICE_N

#define ACCESSORY_CURRENT_SUPPLY 2400 // mA
#define APPLE_BATTERY_CHARGING   1

#define IAP2_USBHOST_HID_INTERFACE_NUMBER INTERFACE_NUMBER_HID


#ifdef IAP_EA_NATIVE_TRANS

#define IAP2_EA_NATIVE_TRANS_PROTOCOL_ID 0
#define IAP2_EA_NATIVE_TRANS_PROTOCOL_NAME "com.xmos.demo"

#define IAP2_EA_NATIVE_TRANS_APP_MATCH_ACTION 1
#define ACCESSORY_APP_PREFERRED_TEAM_ID "2589V44SPS" // XMOS Ltd.

#endif
