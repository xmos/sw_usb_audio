|newpage|

Project Structure
-----------------

.. _proj_build_system:

Build System
++++++++++++

The `XMOS USB Audio Reference Design` software and associated libraries employ the `XMOS XCOMMON` build system. The `XCOMMON` build
system is built on top of the GNU Makefile build system. The `XCOMMON` build system accelerates the development of xCORE 
applications. Instead of having to express dependencies explicitly in Makefiles, users should follow a particular folder
structures and naming convention, from which dependencies are inferred automatically.

The `XCOMMON` build system depends on use of of the tool `XMAKE
<https://www.xmos.ai/documentation/XM-014363-PC-7/html/tools-guide/tools-ref/cmd-line-tools/xmake-manual/xmake-manual.html#xmake>`_ 
specifically. It cannot currently be used with a generic port of GNU Make.


Applications and Libraries
++++++++++++++++++++++++++

The ``sw_usb_audio`` `GIT <https://git-scm.com>`_ repository includes multiple application directories that in turn contain Makefiles that
build into executables. Typically you can expect to see one application directory per hardware platform. 
Applications and there respective hardware platforms are listed in :ref:`proj_app_boards`.

.. _proj_app_boards:

.. list-table:: USB Audio Reference Applications
   :header-rows: 1
   :widths: 20 80

   * - Application
     - Hardware platform
   * - `app_usb_aud_xk_316_mc`
     - xcore.ai USB Audio 2.0 Multi-channel Audio Board
   * - `app_usb_aud_xk_216_mc`
     - xcore-200 USB Audio 2.0 Multi-channel Audio Board
   * - `app_usb_aud_xk_evk_xu316`
     - xcore.ai Evaluation Kit

The code is split into several modules (or `library`) directories, each their own GIT repository. The code for these 
libraries is included in the build by adding the library name to the ``USED_MODULES`` define in an application Makefile. 

Each library has a ``module_build_info`` file that lists it's dependencies in ``DEPENDENT_MODULES``. This allows dependency 
trees and nesting. 

Most of the core code is contained in the `XMOS USB Audio Library` (``lib_xua``). A full list of core dependencies is shown 
in :ref:`proj_core_libs`.

.. _proj_core_libs:

.. list-table:: Core dependencies of USB Audio
   :header-rows: 1
   :widths: 20 80
    
   * - Library
     - Description
   * - `lib_xua`
     - Common code for USB audio applications
   * - `lib_xud`
     - Low level USB device library
   * - `lib_spdif`
     - S/PDIF transmit and receive code
   * - `lib_adat`
     - ADAT transmit and receive code
   * - `lib_mic_array`
     - PDM microphone interface and decimator
   * - `lib_xassert`
     - Lightweight assertions library

.. note:: 

   Some of these core dependencies will have their own dependencies, for example ``lib_mic_array`` depnds on ``lib_xassert`` (see above), ``lib_logging`` (a lightweight print library) and ``lib_dsp`` (a DSP library).

Applications may use additional dependencies to support the hardware platform or add features beyond core functionality.
For example, the application for XK-AUDIO-316-MC uses the additional dependencies listed in :ref:`proj_other_libs`:

.. _proj_other_libs:

.. list-table:: Example additonal dependencies
   :header-rows: 1
   :widths: 20 80
    
   * - Library
     - Description
   * - `lib_i2c`
     - I2C interface, used to configure DACs/ADCs etc
 
