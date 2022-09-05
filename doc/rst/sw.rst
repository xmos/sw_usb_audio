Software Architecture
=====================

The reference applications supplied in ``sw_usb_audio`` use the framework provided in ``lib_xua``. 
These reference design applications customise and extended this framework to provide the required functionality.  
These applications execute on a reference hardware platform.

The applications contained in this repo use ``lib_xua`` in a "code-less" manner. That it, they use 
the ``main()`` function from ``lib_xua`` and customise the code-base as required using build time defines and by 
providing implementations to the various required functions in order to support their hardware. 
Please see ``lib_xua`` documentation for full details.  This document details what these 
customisations are for each application.

