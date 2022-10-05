
.. TODO
.. Description of descriptors

USB Audio Design Guide
=======================

The XMOS USB Audio solution provides *USB Audio Class* compliant devices over USB 2.0 (high-speed 
or full-speed). Based on the XMOS xCORE-200 (XS2) and xCORE.ai (XS3) architectures, it supports USB
Audio Class 2.0 and USB Audio Class 1.0, asynchronous mode (synchronous as an option) and sample 
rates up to 384kHz.

The complete source code, together with the free XMOS XTC development tools and xCORE 
multi-core micro-controller devices, allow the developer to select the exact mix of interfaces 
and processing required.

The XMOS USB Audio solution is deployed as a framework (see `lib_xua``) with reference design 
applications extending and customising this framework. These reference designs have particular 
qualified feature sets and an accompanying reference hardware platform.

This software design guide assumes the reader is familiar with the XC language and xCORE devices. 
For more information see `XMOS Programming Guide 
<https://www.xmos.com/published/xmos-programming-guide>`_.

The reader should also familiarise themselves with the `XMOS USB Device Library (lib_xud)
<https://github.com/xmos/lib_xud/releases/latest>`_ and the `XMOS USB Audio Library (lib_xua)
<https://github.com/xmos/lib_xua/releases/latest>`_

.. note::
    
    The reader should always refer to the supplied `CHANGELOG` and `README` files for known issues
    of a specific release

.. toctree::

    Overview <overview>
    Hardware Platforms <hw>
    Quick Start <quick>
    Programming Guide <programming>
    USB Audio Applications <apps>
    API <api>
    Frequently Asked Questions <faq>




