.. _sec_custom_defines_api:

Custom Defines
--------------



An application using the USB audio framework needs to have a defines file called ``customdefines.h``. The following defines are additional to the standard USB Audio reference design defines for iOS use:

System Feature Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 53 12

   * - Define
     - Description
     - Default
     
   * - ``IAP`` 
     - Define for enabling iOS component
     - defined 

   * - ``IO_EXPANSION`` 
     - Define to enable use of IO expansion interface on port32A rather than port32A directly.
     - defined 

Device Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before submitting ATS Certification Assistant results to Apple, or sending a product to one of Apple's test labs, the following customisations must be made.  These changes should be made in the ``customdefines.h`` file.  These customisation steps should be considered mandatory:

  * Change the USB Vendor ID & Device ID to use the licensee's USB Vendor ID & Device ID. See ``VENDOR_ID`` and ``PID_AUDIO_2`` defines.

  * Change the Vendor string (``VENDOR_STR`` define) to accurately reflect the vendor of the product (This should relate to the ``VENDOR_ID`` value from the USB IF).  Note: This string will also be used to customise strings describing interfaces etc.

  * Change the ``ACCESSORY_FIRMWARE_VERSION`` define to accurately reflect the version number of the firmware (if different from XMOS default).

  * Change the ``ACCESSORY_HARDWARE_VERSION`` define to accurately reflect the version number of the hardware.
  
  * Change the ``ACCESSORY_MODEL_NUMBER`` define to accurately reflect the model number of the accessory.

Note: The USB device and configuration descriptors will automatically be configured to match the various configuration defines set (channel count etc).

.. list-table::
   :header-rows: 1
   :widths: 35 53 12

   * - Define
     - Description
     - Default

   * - ``VENDOR_STR`` 
     - This is used as the Accessory manufacturer in the IDPS process
     - XMOS 

   * - ``VENDOR_ID`` 
     - Vendor ID of the product
     - "0x20B1"

   * - ``PID_AUDIO_1`` 
     -  Product ID of the product used in Audio Class 2.0 mode
     - "0x0002"

   * - ``ACCESSORY_FIRMWARE_VERSION`` 
     - This is used as Accessory firmware version in the IDPS process
     - 

   * - ``ACCESSORY_HARDWARE_VERSION`` 
     - This is used as Accessory hardware version in the IDPS process
     - {1, 1, 0}

   * - ``ACCESSORY_MODEL_NUMBER`` 
     - This is used as Accessory model number in the IDPS process
     - "XR-IOS-USB-AUDIO"
