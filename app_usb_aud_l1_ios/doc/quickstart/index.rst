
.. _usb_audio_interface_qs:

XMOS USB Audio Interface Quick Start Guide
==========================================

.. _usb_audio_interface_qs_introduction:

Introduction
------------

The XMOS USB Audio Interface (XUAI) is designed to facilitate the design of products that require USB connectivity to audio and control interfaces for Mac, PC and iPod, iPhone and iPad devices. Using High Speed USB, it allows digital audio, MIDI and control data to be transferred between the host Mac, PC or iOS device and the XMOS interface.

The XMOS design implements USB Audio 2.0 and USB MIDI interfaces for the widest iOS application compatibility. It will auto-select between USB and 30-pin connections and charge connected iOS devices, including iPad. 

.. _usb_audio_interface_boards:

.. figure:: images/ios-features.*

   XMOS USB Audio Interface

The kit contains the following hardware:

   * An XR-I-AUDIO-ACC board comprising

      * 500MHz XS1-L1 processor

      * High Speed USB interface

      * Audio codec (up to 192kHz)

      * S/PDIF output (up to 192kHz)

      * MIDI interface

      * 2.1A iPad charging circuitry

   * A 30-pin expansion board

   * XTAG-2 debug adapter

   * 12V power supply

|newpage|

The firmware is built from the following software components:

   * USB Audio 2.0

   * XMOS USB Device (XUD)

   * iOS

   * (S/PDIF component is not currently supported in the firmware due to resource limitations)

The kit is supported by the following tools:

   * XMOS Development Tools (11.11.0beta1 onwards), which provide everything you need to develop your own applications.

Platform support:

   * USB Audio 2.0 and USB MIDI are supported natively in OSX and iOS by CoreAudio and CoreMIDI
   * For Windows Drivers, please see: `<http://www.xmos.com/usbaudio2>`_
   
.. _usb_audio_interface_qs_setup_hardware:

Set up the hardware
-------------------

The board has been pre-programmed with the firmware. Updates to this firmware are released periodically, please check with the Avnet website for updated versions. See: `<http://mfi.avnet.com/MFI/>`_

To set up the hardware, follow these steps:

.. steps::

  #. Connect the 30-pin expansion board to the XR-I-AUDIO-ACC board.

  #. Connect the audio output to speakers or headphones.
  
  #. Connect the 12V supply to the board, and connect the power supply to a mains outlet.

.. _usb_audio_interface_qs_try_application:

Try the application
-------------------

Audio output
~~~~~~~~~~~~

.. steps::

  #. Connect an iOS device to the 30-pin connector. Supported iOS devices are: iPad 1 and 2, iPhone 4 and 4S, iPod touch 4th Generation. The device will show the charging icon.

  #. Play audio from the Music or iPod application on the iOS device.

Audio input
~~~~~~~~~~~~

This example uses the Apple GarageBand app.

.. steps::

  #. Connect an iOS device to the 30-pin connector.

  #. Connect an audio source to the LINE IN socket of the board.

  #. Launch the GarageBand app.

  #. Select the Audio Recorder instrument.

  #. Hit the jack icon and turn the Monitor ON. This will route audio from the LINE IN to LINE OUT, via the USB interface on the iOS device. This can be seen on the on-screen VU meter.

  #. Hit the Record button to start GarageBand recording.

MIDI
~~~~

.. steps::

  #. Connect the board to a PC/Mac or iOS device.

  #. Connect the MIDI input connection to a MIDI keyboard or other source.

  #. Run an application such as a MIDI synthesizer (e.g. GarageBand).

  #. The MIDI keyboard will now play audio from the synthesizer on the iOS device. (GarageBand also responds to MIDI controllers for volume and pan which can be seen in the sliders menu).

Auto-switching
~~~~~~~~~~~~~~

.. steps::

  #. Connect the board to a PC or Mac via a standard USB cable and play audio.

  #. Connect an iOS device to the 30-pin connector and audio can be played from this device. The iOS device takes priority if both are connected at the same time.

  #. Disconnect the iOS device and audio will revert to the PC or Mac.

Troubleshooting
~~~~~~~~~~~~~~~

  - Ensure that the iOS device volume is at maximum. Anything less than 90% will be very quiet.

  - The codec on the board will auto-mute so may miss the first note on keyboard.

  - GarageBand produces audio glitches for approximately 8 seconds after the app starts or the interface is connected. Issue reported to Apple.

.. _usb_audio_interface_qs_compile_firmware:

Compile and run the firmware
----------------------------

The firmware is provided as a source code archive. To configure,
you should modify the source code, build the project and load it onto your hardware using the XMOS Development Tools.

.. cssclass:: xde-outside

  .. raw:: html
  
    <ul class="iconmenu">
	<li><a href="http://www.xmos.com/tools">Download the XMOS Development Tools</a></li>
    </ul>
  
  .. only:: latex
  
    The XMOS Development Tools are available from:
   
    `<http://www.xmos.com/tools>`_

  For instructions on installing the tools and XTAG-2 driver, and on starting up the tools, see
  :ref:`installation` and :ref:`get_started`.

  .. warning ::

   The XMOS USB Audio Interface is supported by the 11.11.0beta1 or later tools.

.. _usb_audio_interface_qs_import_firmware:
  
Import the firmware
~~~~~~~~~~~~~~~~~~~

.. cssclass:: xde-outside

  You can rebuild the application either in the XMOS Development Environment (XDE) or on the command-line.
 
  **Create an application using the XDE** |XDE icon|

  .. steps::
  
    #. Choose :menuitem:`File,Import`.
    #. Double-click on the **General** option, select **Existing Projects
       into Workspace** and click **Next**.
    #. In the **Import** dialog box, click **Browse** (next to the **Select
       archive file** text box). In the dialog that appears, browse to the directory 
       in which you downloaded the firmware archive, select it (``.zip`` extension) 
       and click **Open**.
    #. Click **Finish**.
	
       The XDE imports a set of projects into your workspace.
	
  **Create an application on the command line** |CMD icon|
  
  .. steps::
 
    #. Unzip the firmware archive.

  **Customise the application**

The files ``customdefines.h`` contains compile-time configuration options. These options are described in more detail
in the USB Audio Interface Software Guide.

.. _usb_audio_interface_qs_build_and_run_application:

Build and run your application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. cssclass:: xde-inside

  Once you have imported your application, you must build it into an executable binary
  and load this binary onto your hardware. To build and run, follow these steps:

  **To use the XDE** |XDE icon|

.. steps::

  #. Select ``sw_usb_aud_l1_ios`` in the **Project Explorer** and click **Build** |button build|.
  
     The XDE builds the firmware, displaying progress in the **Console**. If there are no errors,
     the XDE adds the compiled binary to the ``Binaries`` folder.

     .. |button build| image:: images/button-build.*
        :iconmargin:

  #. Ensure that your XMOS XTAG-2 debug adaptor is connected to the the XSYS connector 
     on the board, and use a USB cable (not provided) to connect the adapter to your PC.

  #. Choose :menuitem:`Run,Run Configurations`.

  #. In the left panel, double-click **XCore Application**.

     The XDE creates a new configuration and displays the default
     settings in the right panel.

  #. In **Name**, enter a name such as ``New Application``.

  #. The XDE tries to identify the target project and executable for you.
     To select one yourself, click **Browse** to the right of the
     **Project** text box and select ``sw_usb_aud_l1_ios`` in the **Project
     Selection** dialog box. Then click **Search Project** and select the
     executable file in the **Program Selection** dialog box.

  #. Ensure that the **hardware** option is selected, and in the **Target**
     drop-down list select your board.
	 
  #. Click **Run**.

     The XDE loads your executable, displaying any output generated by your
     program in the **Console**.  
     
.. cssclass:: xde-outside

  **To use the command-line tools** |CMD icon|
  
  .. steps:: 

    #. Change to your application directory and enter the following command:
  
       :command:`xmake all`

       The tools build your application. If there are no errors, the tools create a
       binary in the sub-folder ``bin``.

    #. Ensure that your XMOS XTAG-2 debug adaptor is connected to the the XSYS connector 
       on the board, and use a USB cable (not provided) to connect the adapter to your PC.
	   
    #. To run, enter the following command:
  
       :command:`xrun bin/*binary*.xe`

More Information
----------------

For more information please refer to XMOS USB Audio Interface Software Guide.


.. |XDE icon| image:: images/ico-xde.*
   :iconmargin:
   :iconmarginheight: 2
   :iconmarginraise:

.. |CMD icon| image:: images/ico-cmd.*
   :iconmargin:
   :iconmarginheight: 2
   :iconmarginraise:
