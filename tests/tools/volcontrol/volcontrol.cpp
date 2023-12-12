#include <volcontrol.h>

#include <cstdlib>

/* CHAN_COUNT = number of chans + 1 for master volume */
#define MULTI_CHAN_COUNT 11

struct volcontrol {
  enum operation op;
  enum scope scope;
  int fini_index;
  int init_index;
  int channel_index;
  float volume;
  uint32_t clock_src;
#ifdef _WIN32
  TCHAR driver_guid[GUID_STR_LEN];
#endif
};

void help(void) {
    printf("Usage: volcontrol cmd [options]\n\n");
    printf("Commands:\n\n");
    printf("  --resetall fini_index [init_index]     Reset all volumes back to 1.0 (starting at channel init_index), up to but not including fini_index\n");
    printf("  --set [input|output] channel_index volume   Set volume of channel index\n");
    printf("  --showall                    Show all volumes\n");
    printf("  --clock < \"Internal\" | \"SPDIF\" | \"ADAT\" >\n");
#ifdef _WIN32
    printf("  -g<GUID>      Driver GUID string, eg. -g{E5A2658B-817D-4A02-A1DE-B628A93DDF5D}\n");
#endif
    exit(1);
}

void show_all(AudioDeviceHandle deviceID) {
    printf("Output: \n");
    for (int i = 0;i < MULTI_CHAN_COUNT;i++) {
        float vol = getVolume(deviceID, ScopeOutput, (char)i);
        printf("  %d: %f\n", i, vol);
    }
    printf("\nInput: \n");
    for (int i = 0;i < MULTI_CHAN_COUNT;i++) {
        float vol = getVolume(deviceID, ScopeInput, i);
        printf("  %d: %f\n", i, vol);
    }
}

int main(int argc, char const* argv[])
{
    struct volcontrol v;
    memset(&v, 0, sizeof(v));

    if (argc < 2) {
        help();
    }

    int i = 1;
    while (i < argc) {
        if (strcmp(argv[i], "--resetall") == 0) {
            ++i;
            v.op = RESET_ALL;
            if (i >= argc || !isdigit(*argv[i])) {
                help();
            }

            v.init_index = 0;
            v.fini_index = atoi(argv[i]);
            ++i;
            if ((i < argc) && isdigit(*argv[i])) {
                v.init_index = atoi(argv[i]);
                ++i;
            }
        }
        else if (strcmp(argv[i], "--showall") == 0) {
            ++i;
            v.op = SHOW_ALL;
        }
        else if (strcmp(argv[i], "--set") == 0) {
            ++i;
            v.op = SET_VOLUME;
            if (i >= argc) {
                help();
            }
            if (strcmp(argv[i], "input") == 0) {
                ++i;
                v.scope = ScopeInput;
            }
            else if (strcmp(argv[i], "output") == 0) {
                ++i;
                v.scope = ScopeOutput;
            }
            else {
                help();
            }

            if (i >= argc) {
                help();
            }

            v.channel_index = atoi(argv[i]);
            ++i;

            if (i >= argc) {
                help();
            }

            v.volume = (float)atof(argv[i]);
            ++i;
        }
        else if (strcmp(argv[i], "--clock") == 0) {
            ++i;
            v.op = SET_CLOCK;

            if (i >= argc) {
                help();
            }

            if (strcmp(argv[i], "Internal") == 0) {
                v.clock_src = 1;
            }
            else if (strcmp(argv[i], "SPDIF") == 0) {
                v.clock_src = 2;
            }
            else if (strcmp(argv[i], "ADAT") == 0) {
                v.clock_src = 3;
            }
            else {
                printf("Invalid clock: %s\n", argv[i]);
                exit(1);
            }
            ++i;
        }
#ifdef _WIN32
        else if (strncmp(argv[i], "-g", 2) == 0) {
            const char *str_ptr;
            if (strlen(argv[i]) == 2) {
                ++i;
                str_ptr = argv[i];
            } else {
                str_ptr = argv[i] + 2;
            }
            swprintf(v.driver_guid, GUID_STR_LEN, L"%hs", str_ptr);
            ++i;
        }
#endif
        else {
            help();
        }
    }

#ifdef _WIN32
    if (!v.driver_guid[0]) {
        printf("Driver GUID must be specified\n");
        exit(1);
    }
    AudioDeviceHandle deviceID = getXMOSDeviceID(v.driver_guid);
#else
    AudioDeviceHandle deviceID = getXMOSDeviceID();
#endif

    switch(v.op) {
        case NONE:
            help();
            break;

        case RESET_ALL:
            for (int ch = v.init_index; ch < v.fini_index; ch++) {
                setVolume(deviceID, ScopeOutput, ch, 1);
                setVolume(deviceID, ScopeInput, ch, 1);
            }
            break;

        case SET_VOLUME:
            setVolume(deviceID, v.scope, v.channel_index, v.volume);
            break;

        case SHOW_ALL:
            show_all(deviceID);
            break;

        case SET_CLOCK:
            setClock(deviceID, v.clock_src);
            break;
    }

    finish();
    return 0;
}
