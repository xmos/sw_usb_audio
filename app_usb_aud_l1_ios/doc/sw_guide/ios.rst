iOS support
-----------

The iOS component enables the XUAI to operate as an iOS accessory. It adds communication with an iOS device via iAP to identify and authenticate the accessory. The accessory operates as a USB device hence the iOS device must operate in USB host mode. The iOS device is put into host mode by an ID resistor on the board.

Endpoints
+++++++++

iAP messages are transmitted over USB. This requires 3 additional endpoints to implement iAP communication with iOS. The endpoints are:

- 1 interrupt in endpoint
- 1 bulk in endpoint
- 1 bulk out endpoint

Communication with the bulk out endpoint happens directly. The iOS device polls the interrupt in endpoint every 16ms (as defined in it's descriptor) until it receives a zero length packet, then requests from the bulk in endpoint. The endpoints are all implemented in the endpoint buffer and iAP communication is routed through the decouple thread in a similar way to USB MIDI. The decouple thread presents a channel so the iAP component may just send and receive data without dealing with the interrupt endpoint.

Messages between the decoupler and the iAP thread are prepended by the length of the message so that the USB layer can keep variable length iAP messages together.

Threads
+++++++

iAP communication is implemented in one thread which it shares with MIDI (if present). This is to respect the limit of 6 threads. The thread has 2 modes of operation based on the authenticating variable. When authenticating is true it will respond to iAP traffic from the host and will not respond to midi from either side. When authenticating is false is will respond to midi. It leaves authenticating mode after the end of authentication with the iOS device.

Reset
+++++

Reset is signalled from endpoint0 via a shared global flag after enumeration. After reset the accessory must identify and authenticate so it is set into authenticating mode.

Co-processor
++++++++++++

Communication with the Apple authentication coprocessor is via i2c. This uses the same pins as the midi interface. This is selected by the MIDI_EN_N signal on the output shift register. When in authenticating mode this signal is driven high. On leaving authenticating mode it is driven low.

The application supports the 2.0C authentication co-processor only.

iAP
+++

The accessory communicates with the iOS device using iAP General Lingo messages. All messages are sent in individual USB packets.

Identification
++++++++++++++

The accessory identifies itself to the iOS device using the IDPS process. Here it is necessary to report the capabilities and description of the device. It is also possible to associate the device with an iOS app. Please see the Apple MFi Accessory Firmware Specification for more details.

Authentication
++++++++++++++

The accessory identifies itself to the iOS device which in turn requests an authentication certificate. This is retrieved from the authentication co processor and returned over iAP. After the certificate is transmitted the iOS device will issue a challenge to the accessory. The accessory sends this to the coprocessor which responds with a signature. This is returned to the iOS device to complete authentication.

Other messages
++++++++++++++

After authentication the accessory sends the SetAvailableCurrent message to specify that the accessory can provide 2100mA charging current to enable it to charge an iPad.

Automatic USB switching
+++++++++++++++++++++++

The accessory will automatically switch between the 30 pin connector and the USB B connector to change between iOS devices and PC/Mac hosts. The accessory detects presence of an iOS device by polling the 30 pin connector device detect signal via the IO expander. When a device is detected the USB switch is switched over to the Apple 30 pin dock connector. Therefore the iOS device has priority over the PC/Mac. A USB reset happens whenever this switch is made.
