.. _usb_audio_sec_dfu:

Device Firmware Upgrade (DFU)
=============================

The DFU interface handles updates to the boot image of the device. The DFU code is called from 
the Endpoint 0 core.

The interface links USB to the XMOS flash user library (see :ref:`libflash_api`). In Application 
mode the DFU can accept commands to reset the device into DFU mode. There are two ways to do this:

-  The host can send a ``DETACH`` request and then reset the
   device. If the device is reset by the host within a specified
   timeout, it will start in DFU mode (this is initially set to
   one second and is configurable from the host).

-  The host can send a custom user request
   ``XMOS_DFU_RESETDEVICE`` to the DFU interface that 
   resets the device immediately into DFU mode.


Once the device is in DFU mode. The DFU interface can accept commands defined by the 
`DFU 1.1 class specification <http://www.usb.org/developers/devclass_docs/DFU_1.1.pdf*USB>`_. In
addition the interface accepts the custom command ``XMOS_DFU_REVERTFACTORY`` which reverts the active
boot image to the factory image. Note that the XMOS specific command request
identifiers are defined in ``dfu_types.h`` within ``module_dfu``.

