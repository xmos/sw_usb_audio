
.. _usb_audio_sec_valbuild:

Build Configurations
--------------------

Due to the flexibility of the framework there are many different build options.  For example input
and output channel count, Audio Class version, interface types etc. A "build configuration" is 
a set of build options that combine to produce a binary with a certain feature set.

Build configurations are listed in the application Makefile with their associated options, a specific 
configuration can be built via the command line as follows::

    xmake CONFIG=<config name>

To build all supported configurations use the following command::

    xmake all

Configuration Naming Scheme
----------------------------

A naming scheme is employed in each application to link a feature set to a build configuration/binary.  
Depending on the hardware interfaces available variations of the same basic scheme are used.

Each relevant build option is assigned a position in the configuration name, with a character denoting the
options value (normally 'x' is used to denote "off" or "disabled")

For example, :ref:`prog_build_configs_nameing` lists somes example build options.

.. _proj_build_configs_naming:

.. table::  Example build options and naming

 +---------------------+-------------+-------------+
 | Build Option Name   | Options     | Denoted by  |
 +=====================+=============+=============+
 | Audio Class Version | 1 or 2      | 1 or 2      |
 +---------------------+-------------+-------------+
 | MIDI                | on or off   | m or x      |
 +---------------------+-------------+-------------+
 | S/PDIF Output       | on or off   | s or x      |
 +---------------------+-------------+-------------+
 | S/PDIF Input        | on or off   | s or x      |
 +---------------------+-------------+-------------+

For example, in this scheme, a configuration named ``2xsx`` would indicate Audio Class 2.0, MIDI
disabled, S/PDIF output enabled and S/PDIF input disabled.

Some additional letters or numbers may also be used to denote things like channel counts etc. See comments
in the application Makefile for details.

Validated Build Configurations
------------------------------

It is not possible for all build configuration permutations to be exhaustively tested.

The `XMOS USB Audio Reference Design` software defines three levels of quality.

    * **Fully Tested** - the configuration is fully supported and can be placed immediately into to a production environment with high confidence.
    * **Partially Tested** - the configuration is partially tests. It can be places into a production environment with medium confidence. Some additional QA is recommended
    * **Build Tested** - the configuration is guaranteed to build but has not been tested. Full QA is required.

`XMOS` aims to provide fully tested configurations popular device configurations and common customer requirements.

.. note::
    
   It is advised that full QA is a applied to any product regardless of the quality of the configuration it is based on.

Fully tested configurations can be found in the application Makefile. Partially and build tested configurations can be 
found in the ``configs_partial.inc`` and ``configs_build.inc`` files respectively. Using the command ``xmake all`` will
only build fully tested configurations. Partially tested and build tested configurations can be accessed by setting the
``BUILD_PARTIAL_CONFIGS`` and ``BUILD_TEST_CONFIGS`` variable. For example::

    xmake PARTIAL_TEST_CONFIGS=1 all
   




