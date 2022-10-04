# Configs that have been partially tested, but not as comprehensively as those in the Makefile

# Audio Class 2, 2 channels Input, 2 channels Output, no MIDI, no SPDIF
XCC_FLAGS_2i2o2 = $(BUILD_FLAGS) -DMIN_FREQ=44100 -DMAX_FREQ=192000 -DI2S_CHANS_ADC=2 -DI2S_CHANS_DAC=2 -DNUM_USB_CHAN_OUT=2 -DNUM_USB_CHAN_IN=2 -DMIDI=0 -DSPDIF_TX=0
INCLUDE_ONLY_IN_2i2o2 =

