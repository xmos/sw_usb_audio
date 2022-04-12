#ifndef VOLCONTROL_H
#define VOLCONTROL_H

#include <stdint.h>
#include "volcontrol_impl.h"

enum scope {
  ScopeOutput,
  ScopeInput
};

AudioDeviceHandle getXMOSDeviceID(void);
float getVolume(AudioDeviceHandle deviceID, uint32_t scope, uint32_t channel);

void setVolume(AudioDeviceHandle deviceID, uint32_t scope,
	       uint32_t channel, float volume);

void setClock(AudioDeviceHandle deviceID, uint32_t clockId);

void finish(void);
#endif
