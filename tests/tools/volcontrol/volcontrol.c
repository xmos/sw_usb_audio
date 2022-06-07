#include <volcontrol.h>
#include <stdlib.h>

/* CHAN_COUNT = number of chans + 1 for master volume */
#define MULTI_CHAN_COUNT 11

void help(void) {
    printf("Usage: volcontrol cmd [options]\n\n");
    printf("Commands:\n\n");
    printf("  --resetall fini_index [init_index]     Reset all volumes back to 1.0 (starting at channel init_index), up to but not including fini_index\n");
    printf("  --set [input|output] channel_index volume   Set volume of channel index\n");
    printf("  --showall                    Show all volumes\n");
    printf("  --stress init_index n [fini_index]     Stress volumes from channel index init_index upwards (up to but not including fini_index), iterating n times\n");
    printf("  --clock < \"Internal\" | \"SPDIF\" | \"ADAT\" >");
}

void show_all() {
 AudioDeviceHandle deviceID = getXMOSDeviceID();
 printf("Output: \n");
 for (int i = 0;i < MULTI_CHAN_COUNT;i++) {
    printf("  %d: %f\n", i, getVolume(deviceID, ScopeOutput, i));
 }
 printf("\nInput: \n");
 for (int i = 0;i < MULTI_CHAN_COUNT;i++) {
    printf("  %d: %f\n", i, getVolume(deviceID, ScopeInput, i));
 }
}

int main (int argc, char const *argv[])
{
  if (argc < 2) {
    help();
    exit(1);
  }
  if (strcmp(argv[1], "--resetall") == 0) {
    AudioDeviceHandle deviceID = getXMOSDeviceID();
    if (argc < 3) {
      help();
      exit(1);
    }
    int init = 0;
    int fini = atoi(argv[2]);
    if (argc > 3) {
      init = atoi(argv[3]);
    }
    for (int i = init;i < fini;i++) {
     setVolume(deviceID, ScopeOutput, i, 1);
     setVolume(deviceID, ScopeInput, i, 1);
    }
  } else if (strcmp(argv[1], "--stress") == 0) {
    AudioDeviceHandle deviceID = getXMOSDeviceID();
    if (argc < 4) {
      help();
      exit(1);
    }
    int init = atoi(argv[2]);
    int n = atoi(argv[3]);
    int fini = MULTI_CHAN_COUNT;
    if (argc > 4) {
      fini = atoi(argv[4]);
    }
    int val = 1;
    for (int j = 0;j < n;j++) {
      val = 1 - val;
      for (int i = init;i < fini;i++) {
	setVolume(deviceID, ScopeOutput, i, val);
	setVolume(deviceID, ScopeInput, i, val);
      }
    }
  } else if (strcmp(argv[1], "--showall")==0) {
    show_all();
  } else if (strcmp(argv[1], "--set") == 0) {
    if (argc < 5) {
      help();
      exit(1);
    }
    uint32_t scope;
    if (strcmp(argv[2],"input")==0) {
      scope = ScopeInput;
    } else if (strcmp(argv[2], "output")==0) {
      scope = ScopeOutput;
    } else {
      help(); exit(1);
    }
    unsigned i = atoi(argv[3]);
    float vol = atof(argv[4]);
    AudioDeviceHandle deviceID = getXMOSDeviceID();
    setVolume(deviceID, scope, i, vol);
  } else if (strcmp(argv[1], "--clock") == 0) {
    if (argc < 3) {
      help();
      exit(1);
    }
    uint32_t clockId = 0;
    if (strcmp(argv[2], "Internal") == 0) {
      clockId = 1;
    } else if (strcmp(argv[2], "SPDIF") == 0) {
      clockId = 2;
    } else if (strcmp(argv[2], "ADAT") == 0) {
      clockId = 3;
    } else {
      printf("Invalid clock\n");
      exit(1);
    }
    AudioDeviceHandle deviceID = getXMOSDeviceID();
    setClock(deviceID, clockId);

  } else {
    help();
    exit(1);
  }
  finish();
 return 0;
}
