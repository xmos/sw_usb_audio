
#include <platform.h>
#include "mic_array.h"

void set_led_brightness(unsigned ledNo, unsigned ledVal)
{
    
}

void user_pdm_init()
{

}

unsafe void user_pdm_process(mic_array_frame_time_domain * unsafe audio, int output[])
{
    for(unsigned i=0;i<8;i++)
        output[i] = audio->data[i][0];

}

