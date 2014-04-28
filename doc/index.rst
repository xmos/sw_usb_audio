
.. TODO
.. Description of descriptors

USB Audio Design Guide
=======================

The XMOS USB Audio solution provides *USB Audio Class* compliant devices over USB 2.0 (high-speed 
or full-speed). Based on the XMOS XS1 architecture, it supports USB Audio Class 2.0 and USB Audio 
Class 1.0, asynchronous mode and sample rates up to 384kHz.

The complete source code, together with the free XMOS xTIMEcomposer development tools and XCORE 
multi-core micro-controller devices allow the implementer to select the exact mix of interfaces 
and processing required.

The XMOS USB Audio solution is deployed as a framework with reference design applications extending
and customising this framework. These reference designs have particular qualified feature set and 
an accompanying reference hardware platform.

This software design guide assumes the reader is familiar with the XC language and XCORE devices. 
For more information see `Programming XC on XMOS Devices
<https://www.xmos.com/products/documentation/programming-xc-xmos-devices>`_.

The reader should also familiarise themselves with the `XMOS USB Device Library 
<http://www.xmos.com/published/xuddg>`_ and the `XMOS USB Device Design Guide 
<https://www.xmos.com/zh/node/17007?page=9>`_


.. note::
    
    The reader should always refer to the supplied CHANGELOG and README files for known issues etc in a specific release

.. toctree::

    Overview <overview>
    Hardware Platforms <hw>
    Software Architecture <sw>
    Features & Options <features>
    Programming Guide <programming>
    USB Audio Applications <apps>
    API <api>
    Frequently Asked Questions <faq>




