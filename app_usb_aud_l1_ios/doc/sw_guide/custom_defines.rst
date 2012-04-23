.. _usb_audio_interface_sg_custom_defines_api:

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

.. list-table::
   :header-rows: 1
   :widths: 35 53 12

   * - Define
     - Description
     - Default

   * - ``VENDOR_STR`` 
     - This is used as the Accessory manufacturer in the IDPS process
     - XMOS 

   * - ``SERIAL_STR`` 
     - This is used as Accessory serial number in the IDPS process
     - "0000" 

   * - ``ACCESSORY_FIRMWARE_VERSION`` 
     - This is used as Accessory firmware version in the IDPS process
     - 

   * - ``ACCESSORY_HARDWARE_VERSION`` 
     - This is used as Accessory hardware version in the IDPS process
     - {1, 1, 0}

   * - ``ACCESSORY_MODEL_NUMBER`` 
     - This is used as Accessory model number in the IDPS process
     - "XR-IOS-USB-AUDIO"
