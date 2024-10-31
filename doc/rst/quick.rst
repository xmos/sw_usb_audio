|newpage|

***********
Quick Start
***********

.. warning::

    XMOS development boards are typically supplied with no firmware installed. The following steps explain how to
    install the latest firmware on the board and use it. Each step is explained in detail in the following sections.

   #. To download the latest **USB Audio 2.0 Device Software** release, on the `XMOS website USB & Multichannel Audio page <http://www.xmos.com/develop/usb-multichannel-audio>`_,
      follow the `DOWNLOAD SOFTWARE` link. Before downloading the software, review the licence and click **Accept** to initiate the download.

      (Section :ref:`quick_start_firmware`.)

   #. If using a Windows host computer, download the **USB Audio Class 2.0 Evaluation Driver for Windows**.
      On the `XMOS website USB & Multichannel Audio page <http://www.xmos.com/develop/usb-multichannel-audio>`__, follow the `DRIVER SUPPORT` link, and click on `Download`.
      Once downloaded, run the executable and install the driver.

      (Section :ref:`quick_start_windows_driver`.)

   #. Download and install the the `XMOS XTC Tools <http://www.xmos.com/software-tools>`_

      The minimum required XTC Tools version for compiling USB Audio applications can be found in the README. Make sure to download the correct version of the tools.

      (Section :ref:`quick_start_tools`)

   #. Compile the firmware relavant to the available reference hardware platform .

      (Section: :ref:`quick_start_building`)

   #. Connect the board to the development system using the xTAG supplied, and program the firmware onto the board.

      (Section :ref:`quick_start_running`)

   #. Connect audio input and output devices, and play audio.

      (Section :ref:`quick_start_play_audio`)

|newpage|

.. _quick_start_firmware:

USB Audio 2.0 Reference Software
================================

The latest USB Audio 2.0 Reference Design software is available free of charge from XMOS.

When downloading the software for the first time, the user needs to register at:

http://www.xmos.com/

To download the firmware:

   #. On the `XMOS website USB & Multichannel Audio page <http://www.xmos.com/develop/usb-multichannel-audio>`__, follow the `DOWNLOAD SOFTWARE` link

   #. Review the licence agreement and click **Accept**.

   #. Download and save the software when prompted.

The software is distributed as a zip archive containing pre-compiled binaries and source code that can be built using the `XMOS XTC Tools`.

Alternatively, contact a `local sales representative <https://www.xmos.com/find-a-distributor/>`_ for further details:


.. _quick_start_windows_driver:

USB Audio Class 2.0 Evaluation Driver for Windows
=================================================

.. note::

    Since version 10.6.4, macOS natively supports USB Audio Class 2.0 – no driver install is required.

.. note::

    Since version 10, release 1703, Windows natively supports USB Audio Class 2.0 – no driver install is required.

Earlier Window versions only provides support for USB Audio Class 1.0. To use a USB Audio Class 2.0 device under these
Windows versions requires a third party driver.

Developers may also wish to use a third party driver for reasons including:

    * ASIO support
    * Advanced clocking options and controls
    * Improved latency
    * Native DSD (via ASIO)
    * Branding customisation and custom control panels
    * Large channel count devices
    * Etc

`XMOS` therefore provides a free Windows USB Audio driver for evaluation and prototyping and a path to a more feature-rich multichannel production driver from our partner `Thesycon`.

The evaluation driver is available from the `XMOS website <http://www.xmos.com/published/usb-audio-class-20-evaluation-driver-windows>`__:

Further information about the evaluation and production drivers is available in the *USB Audio Class 2.0 Windows Driver Overview* document available on the
`website <http://www.xmos.com/published/usb-audio-20-stereo-driver-windows-overview>`_:


.. _quick_start_tools:

XMOS XTC Development Tools
==========================

The `XMOS XTC tools` provide everything required to develop applications for `xcore multicore microcontrollers` and can be downloaded,
free of charge, from `XMOS XTC tools <https://www.xmos.com/software-tools/>`__. Installation instructions can be found `here <https://xmos.com/xtc-install-guide>`_.
Be sure to pay attention to the section `Installation of required third-party tools
<https://www.xmos.com/documentation/XM-014363-PC-10/html/installation/install-configure/install-tools/install_prerequisites.html>`_.

The `XMOS XTC tools` make it easy to define real-time tasks as a parallel system. They come with standards compliant C and C++ compilers,
language libraries, simulator, symbolic debugger, and runtime instrumentation and trace libraries. Multicore support offers features for
task based parallelism and communication, accurate timing and I/O, and safe memory management. All components work off the real-time multicore
functionality, giving a fully integrated approach.

The XTC tools are required by anyone developing or deploying applications on an `xcore` processor. The tools include:

    * “Tile-level” toolchain (Compiler, assembler, etc)
    * System libraries
    * “Network-level” tools (Multi-tile mapper etc)
    * XSIM simulator
    * XGDB debugger
    * Deployment tools

The tools as delivered are to be used within a command line environment, though may also be integrated with
`VS Code graphical code editor <https://www.xmos.com/documentation/XM-014363-PC/html/installation/install-configure/install-tools/install_prerequisites.html#installation-of-the-vs-code-graphical-code-editor>`_.

.. warning::

    USB Audio applications are compiled using the `XCommon CMake <https://www.xmos.com/file/xcommon-cmake-documentation/?version=latest>`_ build system.
    The minimum XTC tools version that supports XCommon CMake can be found in the README file. Ensure that the firmware is compiled using the correct XTC Tools version.


|newpage|

.. _quick_start_building:

Building the Firmware
=====================

.. note::

    For convenience the release zips provided from XMOS contain precompiled binary (xe) files.

From a command prompt with the XMOS tools available, follow these steps:

    #. Unzip the package zip to a known location

    #. From the relevant application directory (e.g. ``app_usb_aud_xk_audio_316_mc``), execute the commands::

        cmake -G "Unix Makefiles" -B build
        xmake -C build

The above steps will configure and build all of the available and supported build configurations for the application.

The applications are compiled using `XCommon CMake <https://www.xmos.com/file/xcommon-cmake-documentation/?version=latest>`_ which is a `CMake <https://cmake.org/>`_
based build system.
The primary configuration file for the application is the CMakeLists.txt. It is present in the application directory (e.g. ``app_usb_aud_xk_audio_316_mc``).
This file specifies build configs, sources, build options and dependencies.

.. note::

    See ::ref:`proj_build_system` for more details.

.. _quick_start_running:

Running the Firmware
====================

Typically during development the developer wishes to program the device's internal RAM with the application binary directly via JTAG and then execute this application.

To run one of the compiled binaries complete the following steps:

    #. Connect the USB Audio board to the host computer.

    #. Connect the xTAG to the USB Audio board and connect it to the host machine on which the application binary is present via a separate USB cable

    #. Ensure any required external power jacks are connected

Finally, to run the binary on the target, execute a command similar to the following::

    xrun path/to/binary.xe

The device should now present itself as a USB Audio Device on the connected host computer.
It will continue to operate as a USB Audio Device until the target board is power cycled.

Writing the Application Binary to Flash
=======================================

Optionally a binary can be programmed into the boot flash. To do this:

    #. Connect the USB Audio board to the host computer.

    #. Connect the xTAG to the USB Audio board and connect the it to the host machine on which the application binary is present via a separate USB cable

    #. Ensure any required external power jacks are connected

From a command prompt with the XMOS tools available, run the following command::

    xflash path/to/binary.xe

Once flashed the target device will reboot and execute the binary. Power cycling the target board will cause the device to reboot the flashed binary.

.. _quick_start_play_audio:

Playing Audio
=============

    #. Connect the board to any power supply provided (note, some boards will be USB bus powered)

    #. Connect the board to a host with driver support for USB Audio Class using a USB cable

    #. Install the Windows USB Audio 2.0 demonstration driver, if required.

    #. Connect audio input/output devices to the connectors on the board e.g powered speakers

    #. In the audio application, select the XMOS USB Audio device.

    #. Start playing and recording.

Next Steps
==========

Further information on using the board and the `XTC Tools` is available from:

`xcore-200 Multichannel Audio Platform 2v0 Hardware Manual <https://www.xmos.com/file/xcore-200-multichannel-audio-platform-hardware-manual/>`_


`xcore.ai Multichannel Audio Platform 2v0 Hardware Manual <https://www.xmos.com/download/XCORE_AI-Multichannel-Audio-Platform-1V1-Hardware-Manual(1V1).pdf>`_


`XMOS USB Device Library (lib_xud) <https://www.xmos.com/file/lib_xud>`_


`XMOS USB Audio Library (lib_xua) <https://www.xmos.com/file/lib_xua>`_


`XTC Tools User Guide <https://www.xmos.com/documentation/XM-014363-PC/html/>`_

