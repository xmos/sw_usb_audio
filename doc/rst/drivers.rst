
|newpage|

**************
Driver support
**************

The `XMOS` USB Audio Reference design includes support for USB Audio Class (UAC) versions 1.0 and
2.0.
UAC 2.0 includes support for audio over high-speed USB (UAC 1.0 supports full-speed only) and other feature additions.

OS support for UAC 1.0
======================

Support for USB Audio Class 1.0 has been included in macOS and Windows for a number of years.
Most Linux distributions also include support.

OS support for UAC 2.0
======================

Support for USB Audio Class 2.0 is only included in more modern versions of macOS and Windows:

    - Since version 10.6.4 macOS natively supports USB Audio Class 2.0
    - Since version 10, release 1809, Windows natively supports USB Audio Class 2.0

Third party Windows drivers
===========================

For some products it may be desirable to use a third-party driver for Windows.
A number reasons exist as to why this may be desirable:

    - In order to support UAC 2.0 on Windows versions earlier than 10
    - The built-in Windows support is typically designed for consumer audio devices, not for professional audio devices
    - The built in drivers support sound APIs such as WASAPI, DirectSound, MME, but not ASIO.

The XMOS USB Audio Reference design is tested against *Thesycon USB Audio Driver for Windows*. This includes the following
feature-set/benefits:

    - Available for Windows 10 and Windows 11 operating systems
    - Designed for professional audio devices and consumer-style devices
    - Supports ASIO for transparent and low-latency audio streaming
    - Supports Windows sound APIs such as WASAPI, DirectSound, MME
    - Supports high-end audio features such as bit-perfect PCM up to 768 kHz sampling rate, native DSD format (through ASIO) up to DSD1024
    - Supports multiple clock sources such as S/PDIF, ADAT or WCLK inputs
    - Supports MIDI 1.0 class, including MIDI port sharing
    - Supports DFU (Device Firmware Upgrade) and comes with a GUI utility for firmware update
    - Provides a private API for driver control and direct device communication (SDK available)
    - Comes with a control panel application for driver status/control
    - Optionally supports virtual channels (channels available at ASIO and Windows APIs but not implemented in the device)
    - Optionally supports mixing and/or signal processing plugin in the kernel-mode driver
    - Fully supports driver signing, branding and customization including driver installer (Customization will be done by Thesycon)
    - Technical support and maintenance provided by Thesycon
    - Custom features available on request

.. note::

    Many of the benefits listed above apply to both UAC1.0 and UAC2.0 and the Thesycon Driver
    supports both class versions.

