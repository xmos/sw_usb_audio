.. _usb_audio_sec_resource_usage:

Resource Usage
--------------

The following table details the resource usage of each
component of the reference design software.

.. table:: Resource Usage

 +---------------+---------------+---------------------+-------------------------------------+
 |   Component   |   Cores       |   Memory (KB)       |   Ports                             |
 +===============+===============+=====================+=====================================+
 | XUD library   |  1            | 9 (6 code)          | ULPI ports                          |
 |               |               |                     |                                     |
 +---------------+---------------+---------------------+-------------------------------------+
 | Endpoint 0    |  1            | 17.5 (10.5 code)    | none                                |
 +---------------+---------------+---------------------+-------------------------------------+
 | USB Buffering |  1            | 22.5 (1 code)       | none                                |
 +---------------+---------------+---------------------+-------------------------------------+
 | Audio driver  |  1            | 8.5 (6 code)        | See :ref:`usb_audio_sec_audio`      |
 +---------------+---------------+---------------------+-------------------------------------+
 | S/PDIF Tx     |  1            | 3.5 (2 code)        | 1 x 1 bit port                      |
 +---------------+---------------+---------------------+-------------------------------------+
 | S/PDIF Rx     |  1            | 3.7 (3.7 code)      | 1 x 1 bit port                      |
 +---------------+---------------+---------------------+-------------------------------------+
 | ADAT Rx       |  1            | 3.2 (3.2 code)      | 1 x 1 bit port                      |
 +---------------+---------------+---------------------+-------------------------------------+
 | Midi          |  1            | 6.5 (1.5 code)      |   2 x 1 bit ports                   |
 +---------------+---------------+---------------------+-------------------------------------+
 | Mixer         |  2            | 8.7 (6.5 code)      |                                     |
 +---------------+---------------+---------------------+-------------------------------------+
 | ClockGen      |  1            | 2.5 (2.4 code)      |                                     |
 +---------------+---------------+---------------------+-------------------------------------+

.. note::

  These resource estimates are based on the multichannel reference design with
  all options of that design enabled. For fewer channels, the resource
  usage is likely to decrease.

.. note::

    The XUD library requires an 80MIPS core to function correctly
    (i.e. on a 500MHz part only six cores can run).

.. note::

   The ULPI ports are a fixed set of ports on the L-Series
   device. When using these ports, other ports are
   unavailable when ULPI is active. See the `XS1-L Hardware Design Checklist <http://www.xmos.com/published/xs1lcheck>`_  for further details.
