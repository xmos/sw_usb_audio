|newpage|

Project Structure
=================

.. _proj_build_system:

Build System
------------

The `XMOS USB Audio Reference Design` software and associated libraries employ the `XCommon CMake` build system.
The XCommon CMake build system uses CMake to configure and generate the build environment which can then be built using
`xmake <https://www.xmos.ai/documentation/XM-014363-PC-7/html/tools-guide/tools-ref/cmd-line-tools/xmake-manual/xmake-manual.html#xmake>`_.
As part of configuring the build environment, if there are any missing dependencies, XCommon CMake fetches them using ``git``.

Applications and Libraries
--------------------------

The `sw_usb_audio GIT repository <https://github.com/xmos/sw_usb_audio>`_ includes multiple application directories.
Each application directory contains a ``CMakeLists.txt`` file which describes the build configs for that application.
The format of the ``CMakeLists.txt`` is described `here <https://www.xmos.com/documentation/XM-015090-PC-2/html/doc/config_files.html>`_
XCommon CMake uses the ``CMakeLists.txt`` to generate Makefiles that can be compiled using ``xmake`` into executables.
Typically, there's one application directory per hardware platform.
Applications and their respective hardware platforms are listed in :ref:`proj_app_boards`.

.. _proj_app_boards:

.. list-table:: USB Audio Reference Applications
   :header-rows: 1
   :widths: 60 80

   * - Application
     - Hardware platform
   * - `app_usb_aud_xk_316_mc`
     - xcore.ai USB Audio 2.0 Multi-channel Audio Board
   * - `app_usb_aud_xk_216_mc`
     - xcore-200 USB Audio 2.0 Multi-channel Audio Board
   * - `app_usb_aud_xk_evk_xu316`
     - xcore.ai Evaluation Kit

The applications depend on several modules (or `libraries`), each of which have their own GIT repository. The immediate
dependency libraries for the applications are specified by setting the ``APP_DEPENDENT_MODULES`` variable in the
`deps.cmake file <https://github.com/xmos/sw_usb_audio/blob/develop/deps.cmake>`_. ``deps.cmake`` lists the common dependencies for
all the applications and is included in each application's ``CMakeLists.txt``.

The dependency list specified in the ``deps.cmake`` can be extended to add new dependencies. Refer to the XCommon CMake
`Dependency Format documentation <https://www.xmos.com/documentation/XM-015090-PC-2/html/doc/api_reference/dependency_format.html#dependency-format>`_
for more information about adding dependencies.

Each library has a ``lib_build_info.cmake`` which lists the library source, compile flags and dependencies. The library dependencies are
specified in the ``LIB_DEPENDENT_MODULES`` variable in the ``lib_build_info.cmake``.
This allows dependency trees and nesting. XCommon CMake builds up a tree which is traversed depth-first, and populates the sandbox, fetching
any missing dependencies by cloning them from github.

Most of the core code is contained in the `XMOS USB Audio Library (lib_xua) <https://www.xmos.com/file/lib_xua>`_. A full list of core dependencies is shown
in :ref:`the table below <proj_core_libs>`.


.. _proj_core_libs:

|beginfullwidth|

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

|endfullwidth|

.. note::

   Some of these core dependencies will have their own dependencies, for example ``lib_mic_array`` depnds on ``lib_xassert`` (see above), ``lib_logging`` (a lightweight print library) and ``lib_xcore_math`` (a DSP library).


