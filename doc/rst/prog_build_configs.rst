
.. _usb_audio_sec_valbuild:

Build Configurations
--------------------

Due to the flexibility of the reference design software there are a large number of build options.  For example input
and output channel counts, Audio Class version, interface types etc. A "build configuration" is a set of build options 
that combine to produce a binary with a certain feature set.

The following command builds all supported configurations::

    xmake all

Build configurations are listed in the application Makefile with their associated options, a specific 
configuration can be built via the command line as follows::

    xmake CONFIG=<config name>

Once build a corresponding binary for a configuration can be found in the following location::

    <app name>/bin/<app name>_<config name>.xe


Configuration Naming
--------------------

A naming scheme is employed in each application to link features to a build configuration/binary.  
Depending on the hardware interfaces available variations of the same basic scheme are used.

Each relevant build option is assigned a position in the configuration name, with a character denoting the
options value (normally 'x' is used to denote "off" or "disabled")

Some example build options are listed in :ref:`prog_build_configs_naming`.

.. _prog_build_configs_naming:

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

Quality & Testing
-----------------

It is not possible for all build option permutations to be exhaustively tested. The `XMOS USB Audio
Reference Design` software therefore defines three levels of quality:

    * **Fully Tested** - the configuration is fully supported. A product based on it can be immediately put into to a
      production environment with high confidence. Quality assurance (QA) should cover any customised code/functionality.
    * **Partially Tested** - the configuration is partially tested. A product based on it can be put into a production 
      environment with medium confidence. Some additional QA is recommended.
    * **Build Tested** - the configuration is guaranteed to build but has not been tested. Full QA is required.

.. note::

   Typically disabing a function should have no effect on QA. For example, disabling S/PDIF on a fully-tested configuration
   with it enabled should not effect its quality. You should also expect a quality level of a configuration to carry over
   between XMOS device series.. 

`XMOS` aims to provide fully tested configurations for popular device configurations and common customer requirements.

.. note::
    
   It is advised that full QA is a applied to any product regardless of the quality level of the configuration it is based on.

Fully tested configurations can be found in the application Makefile. Partially and build tested configurations can be 
found in the ``configs_partial.inc`` and ``configs_build.inc`` files respectively. Using the command ``xmake all`` will
only build fully tested configurations. Partially tested and build tested configurations can be accessed by setting the
``BUILD_PARTIAL_CONFIGS`` and ``BUILD_TEST_CONFIGS`` variables respectively. For example::

    xmake PARTIAL_TEST_CONFIGS=1 all
   
.. note::

    Pre-release (i.e. alpha, beta or RC) firmware should not be used as basis for a production device and may not be 
    representative of the final release firmware. Additionally, some releases may include feaures of lesser quality level. 
    For example a beta release may contain a feature still at alpha level quality. See application ``README`` 
    for details of any such features.

|newpage|



