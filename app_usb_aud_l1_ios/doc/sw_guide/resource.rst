.. _usb_audio_interface_sg_resource_usage:

Resource Usage
--------------

The following table details the resource usage of each component of the application software. For details of components not described here, see the `USB Audio Software Design Guide <http://www.xmos.com/published/usb-audio-software-design-guide>`_. 

These values are intended to give an indication of the resource usage only. They cannot give an accurate total for the resource usage of the application. Please build the application to determine this.

.. table:: Resource Usage

 +---------------+---------------+---------------------+-------------------------------------+
 |   Component   |   Threads     |   Memory (KB)       |   Ports                             |
 +===============+===============+=====================+=====================================+
 | XUD library   |  1            | 5 (3.5 code)        | ULPI ports                          |
 +---------------+---------------+---------------------+-------------------------------------+
 | Endpoint 0    |  1            | 12.5 (11 code)      | none                                |
 +---------------+---------------+---------------------+-------------------------------------+
 | USB Buffering |  2            | 17.5 (5 code)       | none                                |
 +---------------+---------------+---------------------+-------------------------------------+
 | Audio driver  |  1            | 1 (1 code)          | See USB Audio Software Design Guide |
 +---------------+---------------+---------------------+-------------------------------------+
 | MIDI          |  1            | 6.5 (2 code)        | 2 x 1 bit ports                     |
 +---------------+---------------+---------------------+-------------------------------------+
 | iOS           |  1            | 7 (6 code)          | 2 x 1 bit ports                     |
 +---------------+---------------+---------------------+-------------------------------------+

.. note::

    MIDI and iOS can share thread and ports.

.. note::

    The XUD library requires an 80MIPS thread to function correctly
    (i.e. on a 500MHz parts only six threads can run).

.. note::

   The ULPI ports are a fixed set of ports on the XS1-L1
   device. When using these ports, other ports are
   unavailable when ULPI is active. See the `XS1-L Hardware Design Checklist <http://www.xmos.com/published/xs1lcheck>`_  for further details.
