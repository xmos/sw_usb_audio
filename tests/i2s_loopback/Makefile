# Copyright (c) 2016, XMOS Ltd, All rights reserved
TARGET = xk-audio-216-mc.xn
USED_MODULES = module_usb_audio module_usb_shared module_dfu \
               module_i2c_shared module_i2c_single_port lib_logging

BUILD_FLAGS = -O0 -g -Wall -lflash -D XUD_SERIES_SUPPORT=XUD_X200_SERIES -fxscope

BUILD_FLAGS_i2s_2in_2out_48khz = $(BUILD_FLAGS) -D I2S_MODE_TDM=0 \
  -D ADAT_RX=0 -D ADAT_TX=0 -D SPDIF_RX=0 -D SPDIF_TX=0 -D MIDI=0 \
  -D NUM_USB_CHAN_IN=2 -D NUM_USB_CHAN_OUT=2 -D I2S_CHANS_ADC=2 -D I2S_CHANS_DAC=2 \
  -D DEFAULT_FREQ=48000

BUILD_FLAGS_i2s_2in_2out_192khz = $(BUILD_FLAGS) -D I2S_MODE_TDM=0 \
  -D ADAT_RX=0 -D ADAT_TX=0 -D SPDIF_RX=0 -D SPDIF_TX=0 -D MIDI=0 \
  -D NUM_USB_CHAN_IN=2 -D NUM_USB_CHAN_OUT=2 -D I2S_CHANS_ADC=2 -D I2S_CHANS_DAC=2 \
  -D DEFAULT_FREQ=192000

BUILD_FLAGS_i2s_8in_8out_48khz = $(BUILD_FLAGS) -D I2S_MODE_TDM=0 \
  -D ADAT_RX=0 -D ADAT_TX=0 -D SPDIF_RX=0 -D SPDIF_TX=0 -D MIDI=0 \
  -D NUM_USB_CHAN_IN=8 -D NUM_USB_CHAN_OUT=8 -D I2S_CHANS_ADC=8 -D I2S_CHANS_DAC=8 \
  -D DEFAULT_FREQ=48000

BUILD_FLAGS_i2s_8in_8out_192khz = $(BUILD_FLAGS) -D I2S_MODE_TDM=0 \
  -D ADAT_RX=0 -D ADAT_TX=0 -D SPDIF_RX=0 -D SPDIF_TX=0 -D MIDI=0 \
  -D NUM_USB_CHAN_IN=8 -D NUM_USB_CHAN_OUT=8 -D I2S_CHANS_ADC=8 -D I2S_CHANS_DAC=8 \
  -D DEFAULT_FREQ=192000 \
  -O2 # optimisations to meet timing

BUILD_FLAGS_tdm_8in_8out_48khz = $(BUILD_FLAGS) -D I2S_MODE_TDM=1 \
  -D ADAT_RX=0 -D ADAT_TX=0 -D SPDIF_RX=0 -D SPDIF_TX=0 -D MIDI=0 \
  -D NUM_USB_CHAN_IN=8 -D NUM_USB_CHAN_OUT=8 -D I2S_CHANS_ADC=8 -D I2S_CHANS_DAC=8 \
  -D DEFAULT_FREQ=48000 \
  -O2 # optimisations to meet timing

#XCC_FLAGS_hardware_i2s_2in_2out_48khz    = -D HARDWARE   $(BUILD_FLAGS_i2s_2in_2out_48khz)
#XCC_FLAGS_hardware_i2s_2in_2out_192khz   = -D HARDWARE   $(BUILD_FLAGS_i2s_2in_2out_192khz)
#XCC_FLAGS_hardware_i2s_8in_8out_48khz    = -D HARDWARE   $(BUILD_FLAGS_i2s_8in_8out_48khz)
#XCC_FLAGS_hardware_i2s_8in_8out_192khz   = -D HARDWARE   $(BUILD_FLAGS_i2s_8in_8out_192khz)
#XCC_FLAGS_hardware_tdm_8in_8out_48khz    = -D HARDWARE   $(BUILD_FLAGS_tdm_8in_8out_48khz)

XCC_FLAGS_simulation_i2s_2in_2out_48khz  = -D SIMULATION $(BUILD_FLAGS_i2s_2in_2out_48khz)
XCC_FLAGS_simulation_i2s_2in_2out_192khz = -D SIMULATION $(BUILD_FLAGS_i2s_2in_2out_192khz)
XCC_FLAGS_simulation_i2s_8in_8out_48khz  = -D SIMULATION $(BUILD_FLAGS_i2s_8in_8out_48khz)
XCC_FLAGS_simulation_i2s_8in_8out_192khz = -D SIMULATION $(BUILD_FLAGS_i2s_8in_8out_192khz)
XCC_FLAGS_simulation_tdm_8in_8out_48khz  = -D SIMULATION $(BUILD_FLAGS_tdm_8in_8out_48khz)

XMOS_MAKE_PATH ?= ../..
-include $(XMOS_MAKE_PATH)/xcommon/module_xcommon/build/Makefile.common
