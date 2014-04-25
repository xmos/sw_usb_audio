Getting Started 
================

.. only:: xdehtml

  .. raw:: html
 
     <div class="xde-inside">
     <ul class="iconmenu">
       <li class="xde"><a class="xde-import" href="http://www.xmos.com/automate?automate=ImportComponent&partnum=XM-000011-SW">Import USB Audio L1 Reference Design</a></li>
       <li class="xde"><a class="xde-import" href="http://www.xmos.com/automate?automate=ImportComponent&partnum=XM-000032-SW">Import USB Audio L2 Reference Design</a></li>
     </ul>
     </div>

.. only:: xdehtml

  To build, select the ``app_usb_aud_l1`` or ``app_usb_aud_l2`` project in the
  Project Explorer and click the **Build** icon.

.. cssclass:: xde-outside

  To install the software, open the xTIMEcomposer Studio and
  follow these steps:
   
  #. Choose `File` |submenu| `Import`.
   
  #. Choose `General` |submenu| `Existing Projects into Workspace` and
     click **Next**.
   
  #. Click **Browse** next to `Select archive file` and select
     the file firmware ZIP file.
   
  #. Make sure the projects you want to import are ticked in the
     `Projects` list. Import all the components and whichever
     applications you are interested in.
   
  #. Click **Finish**.

  To build, select the ``app_usb_aud_l1`` or ``app_usb_aud_l2`` project in the
  Project Explorer and click the **Build** icon.

.. cssclass:: cmd-only

  From the command line, you can follow these steps:

    #. To install, unzip the package zip.
  
    #. To build, change into the ``app_usb_aud_l1`` or ``app_usb_aud_l2`` directory and execute the command::
  
        xmake all

The main Makefile for the project is in the
``app_usb_aud_l1`` or ``app_usb_aud_l2`` directory. This file specifies build
options and used modules. The Makefile uses the common build
infrastructure in ``module_xmos_common``. This system includes
the source files from the relevant modules and is documented within
``module_xmos_common``.

Installing the application onto flash
-------------------------------------

To upgrade the firmware you must, firstly:

#. Plug the USB Audio board into your computer.

#. Connect the xTAG-2 to the USB Audio board and plug the xTAG-2
   into your PC or Mac.

To upgrade the flash from xTIMEcomposer Studio, follow these steps:

#. Start xTIMEcomposer Studio and open a workspace.

#. Choose *File* |submenu| *Import* |submenu| *C/XC* |submenu| *C/XC Executable*.

#. Click **Browse** and select the new firmware (XE) file.

#. Click **Next** and **Finish**.

#. A Debug Configurations window is displayed. Click **Close**.

#. Choose *Run* |submenu| *Flash Configurations*.

#. Double-click *xCORE application* to create a new Flash
   configuration.

#. Browse for the XE file in the *Project* and
   *C/XC Application* boxes.

#. Ensure the *xTAG-2* device appears in the target
   list.

#. Click **Flash**.


.. cssclass:: cmd-only

  From the command line:

    #. Open the XMOS command line tools (Desktop Tools Prompt) and
       execute the following command::

         xflash <binary>.xe
