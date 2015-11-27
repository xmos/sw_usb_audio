#!/usr/bin/env python
import xmostest

if __name__ == "__main__":
    xmostest.init()

    xmostest.register_group("sw_usb_audio",
                            "analogue_hw_tests",
                            "Analogue audio hardware tests",
    """
Tests are performed by running the USB Audio reference design software on
XMOS audio hardware platforms. The audio platform under test will be connected
to both a host PC and set of signal generator and analysis devices to provide
and record audio. Tests are run to test the following features:

    * Analogue audio input
    * Analogue audio output
    * Volume changes on input
    * Volume changes on output
    * Codec as master

The tests are run at sample rates of 44.1kHz, 48kHz, 88.2kHz, 96kHz, 176.4kHz and
192kHz. Tests utilise all analogue channels of the board simultaneously.
""")

    xmostest.register_group("sw_usb_audio",
                            "digital_hw_tests",
                            "Digital audio hardware tests",
    """
Tests are performed by running the USB Audio reference design software on
XMOS audio hardware platforms. The audio platform under test will be connected
to both a host PC and set of signal generator and analysis devices to provide
and record audio. Tests are run to test the following features:

    * S/PDIF input
    * S/PDIF output
    * ADAT input
    * ADAT output

The tests are run at sample rates of 44.1kHz, 48kHz, 88.2kHz, 96kHz, 176.4kHz and
192kHz. Tests utilise all digital channels of the board simultaneously.
""")

    xmostest.register_group("sw_usb_audio",
                            "non_audio_hw_tests",
                            "A collection of tests covering non audio related features run on hardware",
    """
Tests are performed by running the USB Audio reference design software on
XMOS audio hardware platforms. The audio platform under test will be connected
to both a host PC and set of signal generator and analysis devices to provide
and record data. Tests are run to test the following features:

    * MIDI input
    * MIDI output
    * DFU
""")

    xmostest.register_group("sw_usb_audio",
                            "stress_hw_tests",
                            "A collection of stress tests run on hardware",
    """
Tests are performed by running the USB Audio reference design software on
XMOS audio hardware platforms. The audio platform under test will be connected
to both a host PC and set of signal generator and analysis devices to provide
and record audio and other data.  Tests are run to test the following features:

    * Analogue audio input
    * Analogue audio output
    * Digital audio input
    * Digital audio output

The tests are run at a sample rates of 192kHz. Tests utilise all audio channels
of the board simultaneously.
""")

    xmostest.register_group("sw_usb_audio",
                            "sw_release_tests",
                            "A collection of tests covering software release checks",
    """
Tests are performed by inspecting the USB Audio reference design source code.
Tests are run to check the following features:

    * USB descriptor bcdDevice definition
""")

    xmostest.runtests()

    xmostest.finish()
