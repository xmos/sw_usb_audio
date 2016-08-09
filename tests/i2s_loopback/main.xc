// Copyright (c) 2016, XMOS Ltd, All rights reserved
#include <platform.h>
#include <stdlib.h>
#include <print.h>
#include <timer.h>
#include "xua_audio.h"

#define DEBUG_UNIT MAIN
#include "debug_print.h"

#ifdef SIMULATION
#define INITIAL_SKIP_FRAMES 10
#define TOTAL_TEST_FRAMES 100
#else
#define INITIAL_SKIP_FRAMES 1000
#define TOTAL_TEST_FRAMES (5 * DEFAULT_FREQ)
#endif

#define SAMPLE(frame_count, channel_num) (((frame_count) << 8) | ((channel_num) & 0xFF))
#define SAMPLE_FRAME_NUM(test_word) ((test_word) >> 8)
#define SAMPLE_CHANNEL_NUM(test_word) ((test_word) & 0xFF)

void generator(chanend c_checker, chanend c_out, client interface i_dfu dfuInterface,
               server audManage_if i_audMan)
{
  unsigned frame_count;
  int underflow_word;
  int fail;
  int i;

  frame_count = 0;

  while (1) {
    underflow_word = inuint(c_out);

#pragma loop unroll
    for (i = 0; i < NUM_USB_CHAN_OUT; i++) {
      outuint(c_out, SAMPLE(frame_count, i));
    }

    fail = inuint(c_checker);

#pragma loop unroll
    for (i = 0; i < NUM_USB_CHAN_IN; i++) {
      outuint(c_checker, inuint(c_out));
    }

    if (frame_count == TOTAL_TEST_FRAMES) {
      if (!fail) {
        debug_printf("PASS\n");
      }
      outct(c_out, AUDIO_STOP_FOR_DFU);
      inuint(c_out);
      exit(0);
    }

    frame_count++;
  }
}

void checker(chanend c_checker, int disable)
{
  unsigned x[NUM_USB_CHAN_IN];
  int last_frame_number;
  unsigned frame_count;
  int fail;
  int i;

  if (disable)
    debug_printf("checker disabled\n");

  /*debug_printf("%s %d/%d %d\n",
    I2S_MODE_TDM ? "TDM" : "I2S", NUM_USB_CHAN_IN, NUM_USB_CHAN_OUT, DEFAULT_FREQ);*/

  fail = 0;
  frame_count = 0;
  last_frame_number = -1;

  while (1) {
    outuint(c_checker, fail);

#pragma loop unroll
    for (i = 0; i < NUM_USB_CHAN_IN; i++) {
      x[i] = inuint(c_checker);
    }

    if (frame_count > INITIAL_SKIP_FRAMES) {
      // check that frame number is incrementing
      if (!disable && SAMPLE_FRAME_NUM(x[0]) != last_frame_number + 1) {
        debug_printf("%d: 0x%x (%d)\n", frame_count, x[0], last_frame_number);
        fail = 1;
      }

      for (i = 0; i < NUM_USB_CHAN_IN; i++) {
        // check channel numbers are 0 to N-1 in a frame
        if (!disable && SAMPLE_CHANNEL_NUM(x[i]) != i) {
          debug_printf("%d,%d: 0x%x\n", frame_count, i, x[i]);
          fail = 1;
        }

        // check frame number doesn't change in a frame
        if (!disable && SAMPLE_FRAME_NUM(x[i]) != SAMPLE_FRAME_NUM(x[0])) {
          debug_printf("%d,%d: 0x%x (0x%x)\n", frame_count, i, x[i], x[0]);
          fail = 1;
        }
      }
    }

    last_frame_number = SAMPLE_FRAME_NUM(x[0]);
    frame_count++;
  }
}

#ifdef SIMULATION
out port p_mclk25mhz = on tile[XUD_TILE]: XS1_PORT_1M;
clock clk_mclk25mhz = on tile[XUD_TILE]: XS1_CLKBLK_1;

void mclk25mhz_start(void);
#endif

int main(void)
{
  interface i_dfu dfuInterface;
  audManage_if i_audMan;
  chan c_checker;
  chan c_out;

  par {
    on tile[AUDIO_IO_TILE]: {
      par {
        audio(c_out, null, null, dfuInterface, i_audMan);
        generator(c_checker, c_out, dfuInterface, i_audMan);
        checker(c_checker, 0);
      }
    }
#ifdef SIMULATION
    on tile[XUD_TILE]: {
      mclk25mhz_start();
      delay_seconds(-1); // tile destructor would stop master clock
    }
#endif
  }

  return 0;
}
