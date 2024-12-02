
|newpage|

**************************
Frequently Asked Questions
**************************

**Why does the USBView tool from Microsoft show errors in the devices descriptors?**

The USBView tool supports USB Audio Class 1.0 only

**How do I set the maximum sample rate of the device?**

See `MAX_FREQ` define in :ref:`sec_xua_conf_api`

**What is the maximum channel count the device can support?**

The maximum channel count of a device is a function of sample-rate and sample-depth.
A standard high-speed USB Isochronous endpoint can handle a 1024 byte packet every microframe (125uS).

It follows then that at 192 kHz the device/hosts expects 24 samples per frame (192000/8000).
When using Asynchronous mode we must allow for +/- one sample, so 25 samples per microframe in this
case.

Assuming 4 byte (32 bit) sample size, the bus expects ((192000/8000)+1) * 4 = 100 bytes per channel
per microframe.
Dividing the maximum packet size by this value yields the theoretical maximum channel count at the
given frequency, that is 1024/100 = 10.24. Clearly this must be rounded down to 10 whole channels.

