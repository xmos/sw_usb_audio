
|newpage|

**********************
USB Audio applications
**********************

The reference applications supplied in ``sw_usb_audio`` use the framework provided in ``lib_xua`` and
provide qualified configurations of the framework which support, and are validated, on an accompanying
reference hardware platform.

These reference design applications customise and extend this framework to provide the required functionality.
This document will now examine in detail how each of the provided applications customise and extend the framework.

The applications contained in this repo use ``lib_xua`` in a "code-less" manner. That is, they use
the ``main()`` function from ``lib_xua`` and customise the code-base as required using build time defines and by
providing implementations to the various required functions in order to support their hardware.

Refer to `lib_xua` <https://www.xmos.com/file/lib_xua>`_ documentation for full details.

.. toctree::

    app_316_mc
    app_216_mc

