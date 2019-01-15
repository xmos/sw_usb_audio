USB Audio 6.15.3 maintenance release
====================================

.. To render, place in a directory alongside xdoc.conf with NEWSTYLE=1 and name
   outer directory by what you want the top right corner label to be. Run xdoc
   upload_issue to set Cognidox ID in bottom right corner. Render with xdoc
   xmospdf.

USB Audio 6.15.3 maintenance release
....................................

Specification
~~~~~~~~~~~~~

Based on most recent general release 6.15.2 (April 2016) with the following additions and changes:

- XUD up to version 2.6.0: bus-powered VBUS, PHY tuning and XS1 #11813
- hide all XS1 applications as they will be untested
- hide legacy build configurations of XS2 MC AUDIO application
- provide three new configurations instead: a 2-channel 'hifi', multichannel I2S slave and TDM
- DFU bug with sensitivity to magic samplerate value (#17473)
- fix DSD clocking: superfluous clock outputs as clock is hardware generated [#]_
- TDM slave sync checking (from XUA 0.2.0 without bug number)
- incomplete reset of output audio buffering on stream format change (Github #39)
- document magic DFU 50 and 500 ms delays

Tested using tools 14.3.3 to prevent second image upgrade issue #17802

.. [#] http://www.beyondlogic.org/usbnutshell/usb6.shtml
