#######
Testing
#######

************
Requirements
************

Test modules that run on a stand-alone device under test (DUT):

* test_dfu

Test modules that require the DUT to be connected to an xCORE-200 MCAB (the audio analyzer harness):

* test_analogue
* test_mixer_ctrl
* test_spdif
* test_volume

Audio Analyzer Harness
======================

For tests that require the audio analyzer harness, all audio connections (analogue, S/PDIF, etc) should be connected
in both directions between the DUT and the harness. The connections should be made in the obvious manner: "out" from
one board to "in" on the other.

Python Requirements
===================

Install the Python modules in requirements.txt in the root of sw_usb_audio with ``pip install -r requirements.txt``.
The ``requirements.txt`` file also lists a recommended (minimum) Python version that is used by our CI system.
It is recommended to use a Python virtual environment.

Software Requirements
=====================

The tests do not build the USB Audio applications, so all board configs that will be tested must have been built
otherwise testcases will fail when the expected application XE isn't present.

Some tests require additional software to be present in particular locations.

* audio analyzer binaries: XEs and host application must be built from the sw_audio_analyzer repo; required for all
  test modules except test_dfu
* xsig: required for all test modules except test_dfu
* xmos_mixer: source is inside lib_xua; required for test_mixer_ctrl
* volcontrol: source is present in the tools subdirectory and can be built in this location; required for all volume
  tests and for S/PDIF input tests (to set the clock source)

The directory structure should look like this::

   | sw_audio_analyzer
   |     |-- app_audio_analyzer_xcore200_mc
   |     |     |-- bin
   |     |     |     |-- app_audio_analyzer_xcore200_mc.xe
   |     |     |     |-- spdif_test
   |     |     |     |     |-- app_audio_analyzer_xcore200_mc_spdif_test.xe
   |     |-- host_xscope_controller
   |     |     |-- bin
   |     |     |     |-- xscope_controller
   | sw_usb_audio
   |     |-- app_usb_aud_xk_316_mc (... and other apps)
   |     |     |-- bin
   |     |     |     |-- 2AMi10o10xssxxx (... and other configs)
   |     |     |     |     |-- app_usb_aud_xk_316_mc_2AMi10o10xssxxx.xe
   |     |-- tests
   |     |     |-- tools
   |     |     |     |-- volcontrol
   |     |     |     |     |-- volcontrol
   |     |     |     |-- xmos_mixer(.exe)
   |     |     |     |-- xsig(.exe)

Optional
--------

When testing on Windows, it is recommended (but not required) to remove the USB device metadata stored by the operating
system between each test, so that the correct device features are detected when changing application configs. The tests
will automatically do this if the USBDeview application is present on the PATH.

***********
Test Levels
***********

There are three test levels:

* smoke: the default level; short duration tests for configs that are defined in an application's Makefile
* nightly: configs from the smoke level are tested with slightly longer duration tests; configs defined in an
  application's configs_partial.inc file are tested with short durations
* weekend: all configs from the nightly level are tested with longer durations

The level can be selected with the ``--level`` option in the pytest command, eg. ``pytest --level nightly``

*************
Running Tests
*************

Tests are run using ``pytest``. The XTAG IDs attached to the DUT(s) and harness(es) must be specified. This can be done
either in the pytest.ini file (using the options that are by default assigned blank values), or using a pytest option
such as ``-o xk_216_mc=RdZ15gCf`` (multiple of these can be provided on the command line).

An option of the form ``<board>_dut`` is the XTAG ID attached to the DUT of the chosen board type.

An option of the form ``<board>_harness`` is the XTAG ID attached to the audio analyzer harness which is connected to
the chosen board type; remember that the harness itself is always an xCORE-200 MCAB.

So if you want to run audio tests with the xk_316_mc board, you must set xk_316_mc_dut and xk_316_mc_harness.

The user may only wants to run a subset of the tests, so the standard pytest ``-k`` option can be used; testcases,
boards and configs are all available as keywords. Some examples of the types of keyword filtering that can be useful::

    pytest -k "analogue_output and 2AMi10o10xssxxx"
    pytest -k "spdif and not 2MSi8o10xxsxxx"
    pytest -k "(analogue or volume) and xk_evk_xu316"
