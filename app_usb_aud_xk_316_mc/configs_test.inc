# Configs that are exclusively used for testing

# DFU upgrade/downgrade testing uses configs built with different version numbers
XCC_FLAGS_upgrade1 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x1
XCC_FLAGS_upgrade2 = $(BUILD_FLAGS) -DBCD_DEVICE_J=0x99 -DBCD_DEVICE_M=0x0 -DBCD_DEVICE_N=0x2

# Windows testing with the built-in driver relies on using product IDs that the Thesycon driver won't bind to
XCC_FLAGS_2AMi8o8xxxxxx_winbuiltin = $(BUILD_FLAGS) -DPID_AUDIO_2=0x001a

# Audio Class 2, Async, I2S Master, 8xInput, 8xOutput, I2S loopback
#INCLUDE_ONLY_IN_2AMi8o8xxxxxx_i2sloop =
#XCC_FLAGS_2AMi8o8xxxxxx_i2sloop = $(BUILD_FLAGS)        -DI2S_LOOPBACK=1  
