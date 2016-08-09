// Copyright (c) 2016, XMOS Ltd, All rights reserved
#ifdef SIMULATION

#include <platform.h>
#include "audiohw.h"
#include "customdefines.h"

extern port p_mclk_in;

extern out port p_mclk25mhz;
extern clock clk_mclk25mhz;

void AudioHwConfig(unsigned samFreq, unsigned mClk, chanend ?c_codec, unsigned dsdMode,
    unsigned sampRes_DAC, unsigned sampRes_ADC)
{
  // nothing
}

void AudioHwInit(chanend ?c_codec)
{
  // nothing
}

void mclk25mhz_start(void)
{
  configure_clock_rate(clk_mclk25mhz, 25, 1);
  configure_port_clock_output(p_mclk25mhz, clk_mclk25mhz);
  start_clock(clk_mclk25mhz);
}

#endif
