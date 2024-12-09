Adding custom code
==================

The flexibility of the `XMOS USB Audio Reference Design` software is such that the reference applications
can be modified to change the feature set or add extra functionality.
Any part of the software can be altered since full source code is supplied.

.. note::

   The reference designs have been verified against a variety of host operating systems at different samples rates.
   Modifications to the code may invalidate the results of this verification and fully retesting the resulting software is strongly recommended.

.. note::

   Developers are encouraged to use a version control system, i.e. `GIT`, to track changes to the
   codebase, however, this is beyond the scope of this document.

The general steps to producing a custom codebase are as follows:

#. Make a copy of the reference application directory (e.g. ``app_usb_aud_xk_316_mc`` or ``app_usb_aud_xk_216_mc``)
   to a separate directory with a different name. Modify the new application to suit the custom requirements. For example:

   * Provide the ``.xn`` file for the target hardware platform by setting the ``APP_HW_TARGET`` in the application's ``CMakeLists.txt``.
   * Update ``xua_conf.h`` with specific defines for the custom application.
   * Add any other custom code in the files as needed.
   * Update the ``main.xc`` to add any custom tasks.

#. Make a copy of any dependencies that require modification (in most cases, this step is unnecessary).
   Update the custom application's ``CMakeLists.txt`` to use these new modules.

#. After making appropriate changes to the code, rebuild and re-flash the device for testing.


.. note::

    Whilst a developer may directly change the code in ``main.xc`` to add custom tasks this may not always
    be desirable. Doing this may make taking updates from `XMOS` non-trivial (the same can be said for any
    custom modifications to any core libraries). Since adding tasks is considered reasonably common, customisation
    defines ``USER_MAIN_CORES`` and ``USER_MAIN_DECLARATIONS`` are made available.

    An example usage is shown in ``app_usb_aud_xk_316_mc/src/extensions/user_main.h``
    In reality the developer must weigh up the inconvenience of using these defines versus the
    inconvenience of merging updates from `XMOS` into a modified codebase.

The following sections show some example changes with a high level overview of how to change the code.

Example: Changing output format
-------------------------------

Customising the digital output format may be required, for example, to support a CODEC that expects sample data right-justified with respect to the word clock.

To achieve this, alter the main audio driver loop in ``xua_audiohub.xc``. After making the alteration, re-test the functionality to ensure proper operation.

Hint, a naive approach would simply include right-shifting the audio data by 7 bits before it is output to the port. This
would of course lose LSB data depending on the sample-depth.

Example: Adding DSP to the output stream
----------------------------------------

To add some DSP requires an extra thread of computation. Depending on the `xcore` device being used, some
existing functionality might need to be disabled to free up a thread (e.g. disable S/PDIF).
There are many ways that DSP processing can be added, the steps below outline one approach:

#. Remove some functionality using the defines in :ref:`sec_xua_conf_api` to free up a thread as required.

#. Add another thread to do the DSP. This core will probably have a single XC channel. This channel can be used to send
   and receive audio samples from the ``XUA_AudioHub()`` task. A benefit of modifying samples here is that samples from
   all inputs are collected into one place at this point. Optionally, a second channel could be used to accept control
   messages that affect the DSP. This could be from Endpoint 0 or some other task with user input - a thread handling
   button presses, for example.

#. Implement the DSP in this thread. This needs to be synchronous (i.e. for every sample received from the ``XUA_AudioHub()``,
   a sample needs to be output back).

