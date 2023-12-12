#ifndef _volcontrol_h_
#include "volcontrol_impl.h"

#include <cstdint>

enum operation {
  NONE,
  RESET_ALL,
  SET_VOLUME,
  SHOW_ALL,
  SET_CLOCK
};

enum scope {
  ScopeOutput,
  ScopeInput
};


#ifdef _WIN32
// GUID strings are 36 characters, plus a pair of braces and NUL-termination
#define GUID_STR_LEN (36+2+1)
AudioDeviceHandle getXMOSDeviceID(TCHAR guid[GUID_STR_LEN]);
#else
AudioDeviceHandle getXMOSDeviceID();
#endif

float getVolume(AudioDeviceHandle deviceID, uint32_t scope, uint32_t channel);

void setVolume(AudioDeviceHandle deviceID, uint32_t scope, 
	       uint32_t channel, float volume);

void setClock(AudioDeviceHandle deviceID, uint32_t clockId);

void finish(void);
#endif  // _volcontrol_h_
