
.. raw:: latex

  \makeoddfoot{singlepage}{}{\mbox{}\\[\onelineskip]{\xmoslightgrey\rule[2mm]{\headwidth}{0.5pt}}\ifpreliminary\begin{picture}(0,0)\put(11,0){\makebox(0,0)[bl]{\includegraphics[width=\textwidth]{preliminary}}}\end{picture}\fi\\\footerpubsummary\companyextra}


####################
USB Audio User Guide
####################

The XMOS USB Audio solution provides *USB Audio Class* compliant devices over USB 2.0 (high-speed
or full-speed). Based on the XMOS xcore-200 (XS2) and xcore.ai (XS3) architectures, it supports USB
Audio Class 2.0 and USB Audio Class 1.0, asynchronous mode (synchronous as an option) and sample
rates up to 384kHz.

The complete source code, together with the free XMOS XTC development tools and xCORE
multi-core micro-controller devices, allow the developer to select the exact mix of interfaces
and processing required.

The XMOS USB Audio solution is deployed as a framework (see `lib_xua <https://www.xmos.com/file/lib_xua>`_) with reference design
applications extending and customising this framework. These reference designs have particular
qualified feature sets and an accompanying reference hardware platform.

This software user guide assumes the reader is familiar with the XC language and xcore devices.
For more information see `XMOS Programming Guide
<https://www.xmos.com/published/xmos-programming-guide>`_.

The reader should also familiarise themselves with the `XMOS USB Device Library (lib_xud)
<https://www.xmos.com/file/lib_xud>`_ and the `XMOS USB Audio Library (lib_xua)
<https://www.xmos.com/file/lib_xua>`_

.. note::

    The reader should always refer to the supplied `CHANGELOG` and `README` files for known issues
    of a specific release

.. toctree::

    Overview <overview>
    Hardware Platforms <hw>
    Driver Support <drivers>
    Quick Start <quick>
    Programming Guide <programming>
    USB Audio Applications <apps>
    API <api>
    Frequently Asked Questions <faq>

