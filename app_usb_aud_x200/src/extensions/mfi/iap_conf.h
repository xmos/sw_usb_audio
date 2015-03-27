#define IAP1 1
#define IAP2 1

/* Include global device configuration defines */
#include "devicedefines.h"

/***** Defines relating to iOS identification *****/
#define ACCESSORY_MODEL_NUMBER   "XK-USB-AUDIO-U8-2C"

#define ACCESSORY_HARDWARE_MAJOR 2
#define ACCESSORY_HARDWARE_MINOR 0
#define ACCESSORY_HARDWARE_POINT 0

/* By default base the iAP version number on USB BCD_DEVICE */
#define ACCESSORY_FIRMWARE_MAJOR BCD_DEVICE_J
#define ACCESSORY_FIRMWARE_MINOR BCD_DEVICE_M
#define ACCESSORY_FIRMWARE_POINT BCD_DEVICE_N

#define ACCESSORY_CURRENT_SUPPLY 2400 // mA
#define APPLE_BATTERY_CHARGING   1
