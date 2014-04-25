.. _usb_audio_sec_clock_recovery:

External Clock Recovery (ClockGen)
----------------------------------

An application can either provide fixed master clock sources via selectable oscillators, clock 
generation IC, etc, to provide the audio master or use an external PLL/Clock Multiplier to
generate a master clock based on reference from the XMOS device.

Using an external PLL/Clock Multiplier allows the design to lock to an external clock source
from a digital stream (e.g. S/PDIF or ADAT input).

The clock recovery core (clockGen) is responsible for generating the reference frequency 
to the Fractional-N Clock Generator. This, in turn, generates the master clock used over the
whole design.

When running in *Internal Clock* mode this core simply generates this clock using a local
timer, based on the XMOS reference clock.

When running in an external clock mode (i.e. S/PDIF Clock" or "ADAT Clock" mode) digital 
samples are received from the S/PDIF and/or ADAT receive core.  

The external frequency is calculated through counting samples in a given period. The 
reference clock to the Fractional-N Clock Multiplier is then generated based on this 
external stream.  If this stream becomes invalid, the timer event will fire to ensure that 
valid master clock generation continues regardless of cable unplugs etc.

This core gets clock selection Get/Set commands from Endpoint 0 via the ``c_clk_ctl`` 
channel.  This core also records the validity of external clocks, which is also queried 
through the same channel from Endpoint 0.


This core also can cause the decouple core to request an interrupt packet on change of 
clock validity.  This functionality is based on the Audio Class 2.0 status/interrupt endpoint
feature.
