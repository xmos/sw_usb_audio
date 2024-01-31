#ifndef __vol_control_impl_win32_h__
#define __vol_control_impl_win32_h__

// define the Windows versions supported by the application
#define _WIN32_WINNT 0x0500     //Windows 2000 or later

// exclude rarely-used stuff from Windows headers
#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <stdio.h>
#include <tchar.h>

// TUSBAUDIO driver API
#include "tusbaudioapi.h"
#include "TUsbAudioApiDll.h"

typedef TUsbAudioHandle AudioDeviceHandle;

#endif // __vol_control_impl_win32_h__
