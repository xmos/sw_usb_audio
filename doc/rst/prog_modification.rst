Adding Custom Code
------------------

The flexibility of the `XMOS USB Audio Reference Design` software is such that you can modify
the reference applications to change the feature set or add extra functionality. 
Any part of the software can be altered since full source code is supplied.

.. note::

   The reference designs have been verified against a variety of host OS types at different samples rates. However, 
   modifications to the code may invalidate the results of this verification and you are strongly encouraged to fully 
   re-test the resulting software.   

.. note:: 

   Developers are encouraged to use a version control system, i.e. `GIT`, to track changes to the codebase, however,
   this is beyond the scope of this document.

The general steps to producing a custom codebase are as follows:

#. Make a copy of the application directory (e.g. ``app_usb_aud_xk_316_mc`` or ``app_usb_aud_xk_216_mc``) 
   you wish to base your code on, to a separate directory with a different name.

#. Make a copy of any dependencies you wish to alter (most of the time
   you probably do not want to do this). Update the Makefile of your
   new application to use these new custom modules.

#. Make appropriate changes to the code, rebuild and re-flash the
   device for testing.

Once you have made a copy, you need to:

#. Provide a ``.xn`` file for your board (updating the ``TARGET`` variable in the Makefile appropriately).
#. Update ``xua_conf.h`` with the specific defines you wish to set.
#. Add any custom code in other files you need.
#. Update ``main.xc`` to add any custom tasks

.. note:: 

    Whilst a developer may directly change the code in ``main.xc`` to add custom tasks this may not always
    be desirable. Doing this may make taking updates from `XMOS` non-trivial (the same can be said for any 
    custom modifications to any core libraries). Since adding tasks is considered a reasonably common customisation
    defines ``USER_MAIN_CORES`` and ``USER_MAIN_DECLARATIONS`` are made available. 
    
    An example usage is shown in ``app_usb_aud_xk_316_mc/src/extensions/user_main.h``
    In reality the developer must weigh up the pain of using these defines versus the pain of merging updates from `XMOS`. 

The following sections show some example changes with a high level overview of how to change the code.

Example: Changing Output Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may wish to customize the digital output format e.g. for a CODEC that expects sample data right-justified with
respect to the word clock.

To do this you need to alter the main audio driver loop in ``xua_audiohub.xc``. After the alteration you need to re-test
the functionality.

Hint, a naive approach would simply include right-shifting the audio data by 7 bits before it is output to the port. This
would of course lose LSB data depending on the sample-depth.

Example: Adding DSP to the Output Stream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add some DSP requires an extra core of computation. Depending on the `xCORE` device being used you may have to disable some
existing functionality to free up a core (e.g. disable S/PDIF). There are many ways that DSP processing can be added,
the steps below outline one approach:

#. Remove some functionality using the defines in :ref:`sec_custom_defines_api` to free up a core as required.

#. Add another core to do the DSP. This core will probably have a single XC channel. This channel can be used to send
   and receive audio samples from the ``XUA_AudioHub()`` task. A benefit of modifying samples here is that samples from 
   all inputs are collected into one place at this point. Optionally, a second channel could be used to accept control 
   messages that affect the DSP. This could be from Endpoint 0 or some other task with user input - a core handling
   button presses, for example.

#. Implement the DSP on this core. This needs to be synchronous (i.e. for every sample received from the ``XUA_AudioHub()``, 
   a sample needs to be outputted back).

