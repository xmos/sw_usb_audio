
.. TODO
.. Description of descriptors
.. DSD
.. 16bit / stream formats
.. App/dir/file arrangement

USB Audio Design Guide
=======================

The XMOS USB Audio solution provides *USB Audio Class* compliant devices over USB 2.0 (high-speed or full-speed).
Based on the XMOS XS1 architecture, it supports USB Audio Class 2.0 and USB Audio Class 1.0, 
asynchronous mode and sample rates up to 384kHz.

The complete source code, together with the free XMOS xTIMEcomposer development tools and XCORE multicore microcontroller devices allow the implementer to select the exact mix of interfaces and processing required.

The XMOS USB Audio solution is deployed as a framework with reference design applications based on this framework provided. These reference designs have particular qualified feature set and an accompanying reference hardware platform.

This software design guide assumes the reader is familiar with the XC
language and XCORE devices. For more information see `Programming
XC on XMOS Devices
<https://www.xmos.com/products/documentation/programming-xc-xmos-devices>`_.

The reader should also familiarise themselves with the XMOS USB Device Library and the XMOS USB Device Design Guide.

The information in this guide is valid with respect to XMOS USB Audio software release version 6.5.0.

.. note::
    
    The reader should always refer  to a specific releases CHANGELOG and README files for known issues etc

.. toctree::

    Overview <overview>
    Hardware Platforms <hw>
    Software Architecture <sw>
..   Programming Guide <programming>
..   API <api>




