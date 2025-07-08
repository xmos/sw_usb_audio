|newpage|

***********
Quick start
***********

.. warning::

    XMOS development boards are typically supplied with no firmware pre-programmed.

The following steps explain how to program the USB Audio software onto a development board and use
it as a USB Audio device.
Each step is explained in detail in the following sections.

#. Download the latest USB Audio 2.0 Device software release from the `XMOS USB & Multichannel Audio webpage <http://www.xmos.com/develop/usb-multichannel-audio>`_, using the `DOWNLOAD SOFTWARE` link.

   * Before downloading the software, review the licence and click **Accept** to initiate the download.

   (Section :ref:`quick_start_firmware`.)

#. If using a Windows host computer, download the `USB Audio Class 2.0 Evaluation Driver for Windows`.

   * On the `XMOS USB & Multichannel Audio developer webpage <http://www.xmos.com/develop/usb-multichannel-audio>`_, follow the `DRIVER SUPPORT` link, and click on `DOWNLOAD EVALUATION DRIVER`. Once downloaded, run the executable and install the driver.

   (Section :ref:`quick_start_windows_driver`.)

#. Download and install the `XMOS XTC Tools <http://www.xmos.com/software-tools>`_

   * The required XTC Tools version for compiling USB Audio applications can be found in the README file supplied in the software package.
     Be sure to download the correct version of the tools.

   (Section :ref:`quick_start_tools`)

#. Compile the software relevant to the available board.

   (Section: :ref:`quick_start_building`)

#. Connect the board to the host machine using two connections: one for the USB Audio device and another for the debug/programming interface, and program the compiled binary onto the board.

   (Section :ref:`quick_start_running`)

#. Connect audio input and output devices, and play audio.

   (Section :ref:`quick_start_play_audio`)

|newpage|

.. _quick_start_firmware:

USB Audio reference software
============================

The USB Audio Reference Design software is available free of charge from `XMOS`.

When downloading the software for the first time, the user needs to register at http://www.xmos.com/.

To download the software:

#. On the `XMOS USB & Multichannel Audio webpage <http://www.xmos.com/develop/usb-multichannel-audio>`__, follow the `DOWNLOAD SOFTWARE` link

#. Review the licence agreement and click **Accept**.

#. Download and save the software when prompted.

The software is distributed as a zip archive containing pre-compiled binaries and source code that can be built using the `XMOS XTC Tools`.

.. _quick_start_windows_driver:

USB Audio Class (UAC) 2.0 evaluation driver for Windows
=======================================================

.. note::

    Since version 10.6.4, macOS natively supports USB Audio Class 2.0 – no driver install is required.

.. note::

    Since version 10, release 1703, Windows natively supports USB Audio Class 2.0 – no driver install is required.

Earlier Window versions only provides support for USB Audio Class (UAC) 1.0. To use a UAC 2.0
device under these Windows versions requires a third party driver.

Developers may also wish to use a third party driver for reasons including:

* ASIO support
* Advanced clocking options and controls - such as synchronisation to an external S/PDIF or ADAT clock
* Improved latency
* Native DSD (via ASIO)
* Branding customisation and custom control panels
* Large channel count devices
* Etc

`XMOS` therefore provides a free Windows USB Audio driver for evaluation and prototyping and a path
to a more feature-rich multichannel production driver from partner `Thesycon`.

The evaluation driver is available via the `USB Audio Driver Support webpage <https://www.xmos.com/software/usb-audio/driver-support/>`_.

.. _quick_start_tools:

XMOS XTC development tools
==========================

The `XMOS XTC tools` provide everything required to develop applications for `xcore multicore microcontrollers` and can be downloaded,
free of charge, from `XMOS XTC tools <https://www.xmos.com/software-tools/>`__. Installation instructions can be found `here <https://xmos.com/xtc-install-guide>`_.
Be sure to pay attention to the section `Installation of required third-party tools
<https://www.xmos.com/documentation/XM-014363-PC-10/html/installation/install-configure/install-tools/install_prerequisites.html>`_.

The `XMOS XTC tools` make it easy to define real-time tasks as a parallel system. They come with standards compliant C and C++ compilers,
language libraries, simulator, symbolic debugger, and runtime instrumentation and trace libraries. Multicore support offers features for
task based parallelism and communication, accurate timing and I/O, and safe memory management. All components work off the real-time multicore
functionality, giving a fully integrated approach.

The XTC tools are required by anyone developing or deploying applications on an `xcore` device.
The tools include:

* “Tile-level” toolchain (Compiler, assembler, etc)
* System libraries
* “Network-level” tools (Multi-tile mapper etc)
* XSIM simulator
* XGDB debugger
* Deployment tools

The tools as delivered are to be used within a command line environment, though may also be integrated with
`VS Code graphical code editor <https://www.xmos.com/documentation/XM-014363-PC/html/installation/install-configure/install-tools/install_prerequisites.html#installation-of-the-vs-code-graphical-code-editor>`_.

|newpage|

.. _quick_start_building:

Building the firmware
=====================

.. note::

    For convenience the release zips provided from XMOS contain precompiled binary (xe) files.

Applications are compiled using `XCommon CMake <https://www.xmos.com/file/xcommon-cmake-documentation/?version=latest>`_ which is a `CMake <https://cmake.org/>`_
based build system.

.. note::

    See :ref:`proj_build_system` for more details.

Each board is supported by a dedicated application located in its own directory. The boards and
their corresponding applications are listed in :numref:`table_quick_start_boards`.

.. _table_quick_start_boards:

.. table:: Boards and their applications
   :align: left

   +---------------------+-------------------------------+
   | Board               | Application                   |
   +=====================+===============================+
   | XK-EVK-XU316        | app_usb_aud_xk_evk_xu316      |
   +---------------------+-------------------------------+
   | XK-AUDIO-216-MC     | app_usb_aud_xk_audio_216_mc   |
   +---------------------+-------------------------------+
   | XK-AUDIO-316-MC     | app_usb_aud_xk_audio_316_mc   |
   +---------------------+-------------------------------+

The primary configuration for applications is in `CMakeLists.txt`. It is present in each
application directory (e.g. ``app_usb_aud_xk_audio_316_mc``).
This file specifies build configs, sources, build options and dependencies.

From a command prompt with the `XMOS` tools available, follow these steps:

#. Unzip the package zip to a known location

#. From the relevant application directory (e.g. ``app_usb_aud_xk_audio_316_mc``), execute the commands::

    cmake -G "Unix Makefiles" -B build
    xmake -j -C build

These steps will configure and build all of the available and supported build configurations for the
application.

.. _quick_start_running:

Running the firmware
====================

To support different feature sets and products, multiple build configurations are provided.
Each configuration produces a distinct binary.
:numref:`table_quick_start_configs` lists the recommended build configurations for initial
evaluation.

|beginfullwidth|

.. _table_quick_start_configs:

.. table:: Applications and suggested build configuration for quick start
   :align: left

   +-------------------------------+---------------------------+-------------------------------------------------------------------+
   | Application                   | Suggested build config    | Description                                                       |
   +===============================+===========================+===================================================================+
   | app_usb_aud_xk_evk_xu316      | 2AMi10o10xssxxx           | UAC 2.0, 10 ch in/out, 8 analogue channels in/out, S/PDIF in/out  |
   +-------------------------------+---------------------------+-------------------------------------------------------------------+
   | app_usb_aud_xk_audio_216_mc   | 2AMi10o10xssxxx           | UAC 2.0, 10 ch in/out, 8 analogue channels in/out, S/PDIF in/out  |
   +-------------------------------+---------------------------+-------------------------------------------------------------------+
   | app_usb_aud_xk_audio_316_mc   | 2AMi2o2xxxxxx             | UAC 2.0, 2 ch in/out, 2 analogue channels in/out                  |
   +-------------------------------+---------------------------+-------------------------------------------------------------------+

|endfullwidth|

During development, it is common to load the application binary directly into the device's internal
RAM via JTAG and execute it immediately.

Boards require two USB connections, one for the USB Audio device and another for a debug interface.
Depending on the board being used, the debug interface will either use an integrated or xTAG.

To run one of the compiled binaries, follow these steps:

#. Connect the USB Audio board to the host computer with a USB cable (typically labelled ``USB``
   or ``USB DEVICE``)

#. Connect the xTAG to the USB Audio board, and then connect the xTAG to the host computer using a
   separate USB cable. *Note: Some boards have an integrated xTAG.*

#. Ensure that any required external power supplies are connected.

Once everything is connected, run the binary on the target device using a command like the
following::

    xrun ./bin/2AMi10o10xssxxx/app_usb_aud_xk_316_mc_2AMi10o10xssxxx.xe

The device should now appear as a USB Audio Device on the host computer. It will continue to
function as such until the board is power cycled.

Writing the application binary to flash
=======================================

If desired, the application binary can be programmed into the device’s boot flash. To do so:

#. Connect the USB Audio board to the host computer with a USB cable (typically labelled ``USB``
   or ``USB DEVICE``)

#. Connect the xTAG to the USB Audio board, then connect the xTAG to the host computer using a
   separate USB cable. *Note: Some boards include an integrated xTAG.*

#. Ensure any required external power supplies are connected.

Once everything is connected, flash the binary on the target device using a command like the
following::

    xflash ./bin/2AMi10o10xssxxx/app_usb_aud_xk_316_mc_2AMi10o10xssxxx.xe

After flashing, the device will automatically reboot and begin executing the application.
Subsequent power cycles will cause the device to boot and run the flashed binary.

.. _quick_start_play_audio:

Playing/recording audio
=======================

To play and record audio using the USB Audio board, follow these steps:

#. Connect the board to a power supply, if required.
   *Note: Some boards are powered via USB and do not require an external supply.*

#. Connect the board to a host system using a USB cable.
   Ensure the host supports USB Audio Class.

#. Install the Windows USB Audio 2.0 demonstration driver, if required.

#. Connect audio input/output devices to the appropriate connectors on the board (e.g.,
   powered speakers, MP3 player). For multichannel boards use input/output 1/2.

#. In your audio application, select the `XMOS` USB Audio device.

#. Begin audio playback and/or recording.


