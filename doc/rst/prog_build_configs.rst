
.. _usb_audio_sec_valbuild:

Build Configurations
====================

Due to the flexibility of the reference design software there are a large number of build options. For example input
and output channel counts, Audio Class version, interface types etc. A "build configuration" is a set of build options
that combine to produce a binary with a certain feature set.

The build configurations are listed in the application ``CMakeLists.txt`` file. The build config names are appended to the ``APP_COMPILER_FLAGS`` variable to list
the options for the compiler to use when compiling all source files for the given build configuration (APP_COMPILER_FLAGS_<build config>).
For example::

    set(APP_COMPILER_FLAGS_2AMi10o10xssxxx ${SW_USB_AUDIO_FLAGS}
                                            -DXUA_SPDIF_TX_EN=1
                                            -DXUA_SPDIF_RX_EN=1)

specifies that the compiler flags used when compiling the ``2AMi10o10xssxxx`` build config are everything defined in the
``SW_USB_AUDIO_FLAGS`` variable plus two extra compiler options for enabling SPDIF TX and RX.

To configure the build configurations, run the ``cmake`` command from the application (e.g. ``app_usb_aud_xk_audio_316_mc``) directory::

    cmake -G "Unix Makefiles" -B build

This will create a directory called ``build`` within the application directory.
The output displayed on stdout for the ``cmake`` command will contain the list of all the build configurations for that application. For example,

.. code-block:: console

    -- Configuring application: app_usb_aud_xk_evk_xu316
    -- Found build configs:
    -- 1AMi2o2xxxxxx
    -- 2AMi2o2xxxxxx

The ``cmake`` command generates the Makefile for compiling the different build configurations. The Makefile is created in the ``build`` directory.

The next step is to run the ``xmake`` command which executes the commands in the Makefile to build the executables corresponding to
the build configs. To build all supported configurations for a given application, from the application directory (e.g. ``app_usb_aud_xk_audio_316_mc``),
run::

    xmake -C build

This will run the ``xmake`` command in the ``build`` directory.
The built executables are stored in the ``<app name>/bin/<config name>`` directories. For example, the ``app_usb_aud_xk_316_mc/bin/2AMi8o8xxxxxx``
directory contains the ``app_usb_aud_xk_316_mc_2ASi8o8xxxxxx.xe`` executable. Note how the name of the executable is set to <app_name>_<config_name>.xe::

    <app name>/bin/<config name>/<app_name>_<config_name>.xe


To build a specific build configuration, after running the ``cmake`` command, run ``xmake`` with the build config specified::

    xmake -C build <build config>

For example::

    xmake -C build 2AMi10o10xssxxx


Configuration Naming
====================

A naming scheme is employed in each application to link features to a build configuration/binary.
Depending on the hardware interfaces available variations of the same basic scheme are used.

Each relevant build option is assigned a position in the configuration name, with a character denoting the
options value (normally 'x' is used to denote "off" or "disabled")

Some example build options are listed in :ref:`prog_build_configs_naming`.

.. _prog_build_configs_naming:

.. list-table:: Example build options and naming
   :header-rows: 1
   :widths: 60 40 40

   * - Build Option Name
     - Options
     - Denoted by
   * - Audio Class Version
     - 1 or 2
     - 1 or 2
   * - USB synchronisation type
     - Asynchronous or Synchronous
     - A or S
   * - Device I2S role
     - Master or Slave
     - M or S
   * - USB IN channels
     -
     - i<number>
   * - USB OUT channels
     -
     - i<number>
   * - MIDI
     - on or off
     - m or x
   * - S/PDIF Output
     - on or off
     - s or x
   * - S/PDIF Input
     - on or off
     - s or x
   * - ADAT Input
     - on or off
     - a or x
   * - ADAT Output
     - on or off
     - a or x
   * - DSD
     - on or off
     - d or x


For example, in this scheme, a configuration named ``2AMi8o8msxxax`` would indicate Audio Class 2.0, USB asynchronous mode, xCore is |I2S| master,
8 USB IN channels, 8 USB OUT channels, MIDI enabled,
S/PDIF input enabled, S/PDIF output disabled, ADAT input disabled, ADAT output enabled and DSD disabled.

See comments in the application CMakeLists.txt for details.

Quality & Testing
=================

It is not possible for all build option permutations to be exhaustively tested. The `XMOS USB Audio
Reference Design` software therefore defines three levels of quality:

    * **Fully Tested** - the configuration is fully supported. A product based on it can be immediately put into to a
      production environment with high confidence. Quality assurance (QA) should cover any customised code/functionality.
    * **Partially Tested** - the configuration is partially tested. A product based on it can be put into a production
      environment with medium confidence. Some additional QA is recommended.
    * **Build Tested** - the configuration is guaranteed to build but has not been tested. Full QA is required.

.. note::

   Typically disabling a function should have no effect on QA. For example, disabling S/PDIF on a fully-tested configuration
   with it enabled should not affect its quality.

`XMOS` aims to provide fully tested configurations for popular device configurations and common customer requirements.

.. note::

   It is advised that full QA is applied to any product regardless of the quality level of the configuration it is based on.

Fully tested configurations can be found in the application CMakeLists.txt. Partially and build tested configurations can be
found in the ``configs_partial.cmake`` and ``configs_build.cmake`` files respectively.

Running ``cmake -G "Unix Makefiles" -B build`` will only configure the fully tested configurations and following this
up with the ``xmake -C build`` command will build only these.

To configure and build the partially tested configs in addition to the fully tested ones, run cmake with the ``PARTIAL_TESTED_CONFIGS`` variable set to 1::

    cmake -G "Unix Makefiles" -B build -DPARTIAL_TESTED_CONFIGS=1

Following this with the ``xmake -C build`` command will build both fully and partially tested configs.

Similarly to also build the build tested configs along with the fully tested ones, run cmake with ``BUILD_TESTED_CONFIGS`` set to 1, followed by the ``xmake`` command::

    cmake -G "Unix Makefiles" -B build -DBUILD_TESTED_CONFIGS=1

Note that setting ``BUILD_TESTED_CONFIGS`` to 1 internally also set the ``PARTIAL_TESTED_CONFIGS`` to 1. So running ``cmake`` with ``BUILD_TESTED_CONFIGS``
set to 1 will configure the fully tested, partially tested and build-only configs and following this up with an ``xmake -C build`` will build all the 3 types
of configs.


.. note::

    Pre-release (i.e. alpha, beta or RC) firmware should not be used as basis for a production device and may not be
    representative of the final release firmware. Additionally, some releases may include features of lesser quality level.
    For example a beta release may contain a feature still at alpha level quality. See application ``README``
    for details of any such features.

.. note::

    Due to the similarities between the `xCORE-200` and `xCORE.ai` series feature sets, it is fully expected that all
    listed `xCORE-200` series configurations will operate as expected on the `xCORE.ai` series and vice versa. It is therefore
    expected that a quality level of a configuration will migrate between XMOS device series.


|newpage|



