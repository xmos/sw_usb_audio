
.. _usb_audio_sec_valbuild:

Validated Build Options
-----------------------

Due to the flexibility of the framework there are many different build options.  For example input and output channel count, 
Audio Class version, interface types etc

This results in many potential build configuration permutations.  It is not possible for all of these to be exhaustively tested.
XMOS therefore test a subset of build configurations for proper behaviour, these are based on popular device configurations.

Please see the various reference design sections for relevant validated build configurations.

When a reference design project is compiled all configurations are automatically built.  A naming scheme is employed to link a feature set to binaries.  This scheme is described in the next section.

Binary Naming Scheme
--------------------

This section describes the naming scheme for the default binaries generated for each build configuration

Each relevant build option is assigned a position in the string, with a character denoting the options value (normally 'x' is used to denote "off" or "disabled"

For example, :ref:`l1_build_options` lists the build options for the single tile L-Series Reference Design.

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

For example a binary named 2ioxs would indicate Audio Class 2.0 with input and output enabled, MIDI disabled, SPDIF output enabled.

