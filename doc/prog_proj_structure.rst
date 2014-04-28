Project Structure
-----------------

Applications and Modules
++++++++++++++++++++++++

The code is split into several module directories. The code for these
modules can be included by adding the module name to the
``USED_MODULES`` define in an application Makefile:

.. list-table:: Modules used by USB Audio

 * - module_xud
   - Low level USB library
 * - module_usb_shared
   - Common code for USB applications
 * - module_usb_device
   - Common code for USB device applications
 * - module_usb_audio
   - Common code for USB audio applications
 * - module_spdif_tx
   - S/PDIF transmit code
 * - module_spdif_rx
   - S/PDIF receive code
 * - module_adat_rx
   - ADAT receive code
 * - module_usb_midi
   - MIDI I/O code
 * - module_dfu 
   - Device Firmware Upgrade code

There are multiple application directories that contain Makefiles that
build into executables:

.. list-table:: USB Audio Reference Applications

  * - app_usb_aud_l1
    - USB Audio 2.0 Reference Design application
  * - app_usb_aud_l2
    - USB Audio 2.0 Multichannel Reference Design application
  * - app_usb_aud_skc_u16
    - U16 SliceKit with Audio Slice application
  * - app_usb_aud_xk_u8_2c
    - Multi-function Audio board application
  * - app_usb_aud_skc_su1
    - DJ kit application
 

 
