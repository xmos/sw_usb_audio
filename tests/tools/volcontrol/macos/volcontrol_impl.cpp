#include <volcontrol.h>
#import <AudioToolbox/AudioServices.h>

#include <string.h>

const char *gClockNameString[3] =
{
  "Internal",
  "S/PDIF",
  "ADAT",
};

UInt32 getXMOSDeviceID(void)
{
  AudioObjectPropertyAddress propertyAddress = {
    kAudioHardwarePropertyDevices,
    kAudioObjectPropertyScopeGlobal,
    kAudioObjectPropertyElementMaster
  };

  UInt32 dataSize = 0;
  OSStatus status = AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &propertyAddress, 0, NULL, &dataSize);
  if(kAudioHardwareNoError != status) {
    fprintf(stderr, "AudioObjectGetPropertyDataSize (kAudioHardwarePropertyDevices) failed: %i\n", status);
    return kAudioObjectUnknown;
  }
  UInt32 deviceCount = (dataSize / sizeof(AudioDeviceID));
  AudioDeviceID *audioDevices = (AudioDeviceID *) malloc(dataSize);
  if(NULL == audioDevices) {
    fputs("Unable to allocate memory", stderr);
    return kAudioObjectUnknown;
  }

  status = AudioObjectGetPropertyData(kAudioObjectSystemObject, &propertyAddress, 0, NULL, &dataSize, audioDevices);
  if(kAudioHardwareNoError != status) {
    fprintf(stderr, "AudioObjectGetPropertyData (kAudioHardwarePropertyDevices) failed: %i\n", status);
    free(audioDevices), audioDevices = NULL;
    return kAudioObjectUnknown;
  }

  // Iterate through all the devices and determine which are input-capable
  propertyAddress.mScope = kAudioDevicePropertyScopeInput;
  for(UInt32 i = 0; i < deviceCount; ++i) {
    // Query device UID
    CFStringRef deviceUID = NULL;
    dataSize = sizeof(deviceUID);
    propertyAddress.mSelector = kAudioDevicePropertyDeviceUID;
    status = AudioObjectGetPropertyData(audioDevices[i], &propertyAddress, 0, NULL, &dataSize, &deviceUID);
    if(kAudioHardwareNoError != status) {
      fprintf(stderr, "AudioObjectGetPropertyData (kAudioDevicePropertyDeviceUID) failed: %i\n", status);
      continue;
    }

    // Query device name
    CFStringRef deviceName = NULL;
    dataSize = sizeof(deviceName);
    propertyAddress.mSelector = kAudioDevicePropertyDeviceNameCFString;
    status = AudioObjectGetPropertyData(audioDevices[i], &propertyAddress, 0, NULL, &dataSize, &deviceName);
    if(kAudioHardwareNoError != status) {
      fprintf(stderr, "AudioObjectGetPropertyData (kAudioDevicePropertyDeviceNameCFString) failed: %i\n", status);
      continue;
    }

    // Query device manufacturer
    CFStringRef deviceManufacturer = NULL;
    dataSize = sizeof(deviceManufacturer);
    propertyAddress.mSelector = kAudioDevicePropertyDeviceManufacturerCFString;
    status = AudioObjectGetPropertyData(audioDevices[i], &propertyAddress, 0, NULL, &dataSize, &deviceManufacturer);
    if(kAudioHardwareNoError != status) {
      fprintf(stderr, "AudioObjectGetPropertyData (kAudioDevicePropertyDeviceManufacturerCFString) failed: %i\n", status);
      continue;
    }

    if (CFStringFind(deviceManufacturer,
      CFStringCreateWithCString(NULL,
      "XMOS",
      kCFStringEncodingMacRoman),
      0).location == kCFNotFound)
      continue;

    #if 0
    printf("Name = %s\n",CFStringGetCStringPtr(deviceName, kCFStringEncodingMacRoman));
    printf("Manufacturer = %s\n",CFStringGetCStringPtr(deviceManufacturer, kCFStringEncodingMacRoman));
    #endif
    return audioDevices[i];
  }
  printf("Cannot find XMOS device\n");
  exit(1);
}


AudioDeviceID getDefaultOutputDeviceID()
{
  AudioDeviceID outputDeviceID = kAudioObjectUnknown;

  // get output device device
  OSStatus status = noErr;
  AudioObjectPropertyAddress propertyAOPA;
  propertyAOPA.mScope = kAudioObjectPropertyScopeGlobal;
  propertyAOPA.mElement = kAudioObjectPropertyElementMaster;
  propertyAOPA.mSelector = kAudioHardwarePropertyDefaultOutputDevice;

  if (!AudioHardwareServiceHasProperty(kAudioObjectSystemObject, &propertyAOPA))
    {
      printf("Cannot find default output device!");
      return outputDeviceID;
    }

  status = AudioHardwareServiceGetPropertyData(kAudioObjectSystemObject, &propertyAOPA, 0, NULL, (UInt32[]){sizeof(AudioDeviceID)}, &outputDeviceID);

  if (status != 0)
    {
      printf("Cannot find default output device!");
    }
  return outputDeviceID;
}

 float getVolume (AudioDeviceID deviceID, UInt32 scope, UInt32 channel)
{
  AudioObjectPropertyAddress prop = {
    kAudioDevicePropertyVolumeScalar,
    scope == ScopeOutput ? kAudioDevicePropertyScopeOutput : kAudioDevicePropertyScopeInput,
    channel
  };

  if(!AudioObjectHasProperty(deviceID, &prop)) {
      printf("Audio device has no volume property\n");
      exit(1);
  }
  Float32 volume;
  UInt32 dataSize = sizeof(volume);
  OSStatus result = AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &dataSize, &volume);

  if(kAudioHardwareNoError != result) {
      printf("Error getting volume\n");
      exit(1);
    }

  return volume;
}

 void setVolume (AudioDeviceID deviceID, UInt32 scope,
                 UInt32 channel, Float32 volume)
{
  AudioObjectPropertyAddress prop = {
    kAudioDevicePropertyVolumeScalar,
    scope == ScopeOutput ? kAudioDevicePropertyScopeOutput : kAudioDevicePropertyScopeInput,
    channel
  };

  if(!AudioObjectHasProperty(deviceID, &prop)) {
      printf("Audio device has no volume property\n");
      exit(1);
  }
  UInt32 dataSize = sizeof(volume);
  OSStatus result = AudioObjectSetPropertyData(deviceID, &prop, 0, NULL, dataSize, &volume);

  if(kAudioHardwareNoError != result) {
      printf("Error setting volume\n");
      exit(1);
    }

}

void setClock(AudioDeviceHandle deviceID, uint32_t clockId)
{
  AudioObjectPropertyAddress prop = {
    kAudioDevicePropertyClockSources,
    kAudioDevicePropertyScopeInput,
  };

  if (!AudioObjectHasProperty(deviceID, &prop)) {
      printf("Audio device has no clock property\n");
      exit(1);
  }

  UInt32 numClockSources = 0;
  UInt32 dataSize = 0;

  OSStatus result = AudioObjectGetPropertyDataSize(deviceID, &prop, 0, NULL, &dataSize);
  if(kAudioHardwareNoError != result) {
    printf("Error getting number of clocks\n");\
    exit(1);
  }
  numClockSources = dataSize / (sizeof(UInt32));
  UInt32 clockSources[numClockSources];

  if(numClockSources == 0) {
    printf("Error: No clock sources available\n");
    exit(1);
  }

  result = AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &dataSize, clockSources);
  if(kAudioHardwareNoError != result) {
    printf("Error getting the available clock sources\n");
    exit(1);
  }

  // Get the names of the clock sources
  printf("Found %d clock sources\n", numClockSources);

  for(int i = 0; i < numClockSources; i++) {
    printf("Clock %d = %u; ", i, clockSources[i]);
    prop.mSelector = kAudioDevicePropertyClockSourceNameForIDCFString;
    prop.mScope = kAudioDevicePropertyScopeInput;
    CFStringRef clockName = NULL;
    UInt32 dataSize = sizeof(clockName);

    AudioValueTranslation avt;
    avt.mInputData = &clockSources[i];
    avt.mInputDataSize = sizeof(UInt32);
    avt.mOutputData = &clockName;
    avt.mOutputDataSize = dataSize;
    dataSize = sizeof(avt);

    result = AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &dataSize, &avt);
    if(kAudioHardwareNoError != result) {
      printf("Error getting clock name, %d\n", result);
      exit(1);
    }
    printf("%s\n", CFStringGetCStringPtr(clockName, kCFStringEncodingMacRoman));

    if (CFStringFind(clockName,
      CFStringCreateWithCString(NULL,
      gClockNameString[clockId - 1],
      kCFStringEncodingMacRoman),
      0).location == kCFNotFound)
    {
      // Not the right clock
      continue;
    }
    // Found the required clock
    // Select the clock

    prop.mSelector = kAudioDevicePropertyClockSource;

    result = AudioObjectSetPropertyData(deviceID, &prop, 0, NULL, sizeof(UInt32), &clockSources[i]);
    if(kAudioHardwareNoError != result) {
      printf("Error setting clock to %s\n", gClockNameString[clockId - 1]);
      exit(1);
    } else {
      sleep(1);
      // Check if the clock stick
      UInt32 currentClockSource = 0;
      result = AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &dataSize, &currentClockSource);
      if(kAudioHardwareNoError != result) {
        printf("Error checking the set clock source\n");
        exit(1);
      }
      printf("Current clock ID: %u\n", currentClockSource);
      if(currentClockSource != clockSources[i]) {
        // Clock didn't stick
        printf("Error '%s' clock is not valid yet\n", gClockNameString[clockId - 1]);
        exit(1);
      }
      printf("Clock source set to %s\n", gClockNameString[clockId - 1]);
      return;
    }
  }
  // Looks like clock not found
  printf("Clock source '%s' not found\n", gClockNameString[clockId - 1]);
  exit(1);
}

void setStreamFormat(AudioDeviceHandle deviceID, uint32_t scope, unsigned sample_rate, unsigned num_chans, unsigned bit_depth) {
  UInt32 size;
  int err = AudioDeviceGetPropertyInfo(deviceID, 0, scope == ScopeInput, kAudioDevicePropertyStreamFormats, &size, NULL);
  if (kAudioHardwareNoError != err) {
    printf("Error: failed to get supported stream formats, error %d\n", err);
    exit(1);
  }

  int num_formats = size / sizeof(AudioStreamBasicDescription);
  AudioStreamBasicDescription *descs = (AudioStreamBasicDescription *)calloc(num_formats, sizeof(AudioStreamBasicDescription));
  if (!descs) {
    printf("Error: failed to allocate memory for supported stream formats\n");
    exit(1);
  }

  err = AudioDeviceGetProperty(deviceID, 0, scope == ScopeInput, kAudioDevicePropertyStreamFormats, &size, descs);
  if (kAudioHardwareNoError != err) {
    printf("Error: failed to populate supported stream format data, error %d\n", err);
    goto err_free;
  }

  int i;
  for (i = 0; i < num_formats; ++i) {
    if (((unsigned)descs[i].mSampleRate == sample_rate) && (descs[i].mChannelsPerFrame == num_chans) && (descs[i].mBitsPerChannel == bit_depth)) {
      break;
    }
  }
  if (i == num_formats) {
    printf("Error: no supported format matching %u channels, %u bit resolution at sample rate %u\n", num_chans, bit_depth, sample_rate);
    goto err_free;
  }

  err = AudioDeviceSetProperty(deviceID, 0, 0, scope == ScopeInput, kAudioDevicePropertyStreamFormat, sizeof(AudioStreamBasicDescription), &descs[i]);
  if (kAudioHardwareNoError != err) {
    printf("Error: failed to set stream format, error %d\n", err);
    goto err_free;
  }

  free(descs);
  return;

err_free:
  free(descs);
  exit(1);
}

void finish(void) {

}
