Adding Custom Code
------------------

The flexibility of the USB audio solution means that you can modify
the reference applications to change the feature set or add extra
functionality. Any part of the software can be altered with the exception of the
XUD library. 

.. note::

   The reference designs have been verified against a variety of host
   OS types, across different samples rates. However, modifications to
   the code may invalidate the results of this verification and you are strongly encouraged to retest the resulting software.   

The general steps are:

#. Make a copy of the eclipse project or
   application directory (``app_usb_aud_l1`` or ``app_usb_aud_l2``) 
   you wish to base your
   code on, to a separate directory with a different name.

#. Make a copy of any modules you wish to alter (most of the time
   you probably do not want to do this). Update the Makefile of your
   new application to use these new custom modules.

#. Make appropriate changes to the code, rebuild and reflash the
   device for testing.

Once you have made a copy, you need to:

#. Provide a ``.xn`` file for your board (updating the `TARGET`
   variable in the Makefile appropriately).
#. Update ``device_defines.h`` with the specific defines you wish
   to set.
#. Update ``main.xc``.
#. Add any custom code in other files you need.

The following sections show some example changes with a high level
overview of how to change the code.

Example: Changing output format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may wish to customize the digital output format e.g. for a
CODEC that expects sample data left justified with respect to the
word clock.

To do this you need to alter the main audio driver loop in
``audio.xc``. After the alteration you need to re-test the
functionality. The XMOS Timing Analyzer can help
guarantee that your changes do not break the timing requirement of
this core.

Example: Adding DSP to output stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add some DSP requires an extra core of computation, so some
existing functionality needs to be removed (e.g. S/PDIF). Follow
these steps to update the code:


#. Remove some functionality using the defines in
   :ref:`usb_audio_sec_custom_defines_api`.

#. Add another core to do the DSP. This core will probably have
   three XC channels: one channel to receive samples from decoupler
   core and another to output to the audio driver---this way the
   core 'intercepts' audio data on its way to the audio driver; the
   third channel can receive control commands from Endpoint 0.

#. Implement the DSP on this core. This needs to be synchronous
   (i.e. for every sample received from the decoupler, a sample needs
   to be outputted to the audio driver).

#. Update the Endpoint 0 code to accept custom requests to the audio
   class interface to control the DSP. It can then forward the changes
   onto the DSP core.

#. Update host drivers to use these custom requests.



