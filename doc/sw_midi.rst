MIDI
----

The MIDI driver implements a 31250 baud UART input and output. On receiving 32-bit USB MIDI events
from the ``buffer`` core, it parses these and translates them to 8-bit MIDI messages which are sent
over UART. Similarly, incoming 8-bit MIDI messages are aggregated into 32-bit USB-MIDI events an
passed on to the ``buffer`` core. The MIDI core is implemented in the file ``usb_midi.xc``.
