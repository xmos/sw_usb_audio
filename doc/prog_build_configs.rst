
Build Configurations
--------------------

Due to the flexibility of the framework there are many different build options.  For example input
and output channel count, Audio Class version, interface types etc. A "build configuration" is 
a set of build options that combine to produce a certain feature set.

Build configurations are listed in the application makefile with their associated options, they can 
be built within the xTIMEComposer GUI or via the command like as follows::

    xmake CONFIG=<config name>

When a reference design application is compiled using "build all" (`xmake all` on command line) all
configurations are automatically built.  

A naming scheme is employed in each application to link a feature set to a build configuration/binary.  This scheme is described
in the next section.

.. _usb_audio_sec_valbuild:

Configuration Naming Scheme
----------------------------

This section describes the naming scheme for the default configurations (and therefore binaries) 
generated for each build configuration

Each relevant build option is assigned a position in the string, with a character denoting the
options value (normally 'x' is used to denote "off" or "disabled")

For example, :ref:`l1_build_options` lists the build options for the single tile L-Series Reference
Design.

.. _l1_build_options:

.. table::  Single tile L-Series build options

 +---------------------+-------------+-------------+
 | Build Option Name   | Options     | Denoted by  |
 +=====================+=============+=============+
 | Audio Class Version | 1 or 2      | 1 or 2      |
 +---------------------+-------------+-------------+
 | Audio Input         | on or off   | i or x      |
 +---------------------+-------------+-------------+
 | Audio Output        | on or off   | o or x      |
 +---------------------+-------------+-------------+
 | MIDI                | on or off   | m or x      |
 +---------------------+-------------+-------------+
 | S/PDIF Output       | on or off   | s or x      |
 +---------------------+-------------+-------------+

For example a binary named 2ioxs would indicate Audio Class 2.0 with input and output enabled, MIDI
disabled, SPDIF output enabled.

Validated Build Options
-----------------------

It is not possible for all possible build configuration permutations to be exhaustively tested.
XMOS therefore test a subset of build configurations for proper behaviour, these are based on
popular device configurations.

Please see the various reference design sections for relevant validated build configurations.

