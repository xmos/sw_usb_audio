XMOS USB Audio 2.0 Reference Design Change Log
..............................................

:Latest release: 6.0.0alpha0
:Maintainer: Ross Owen
:Description: USB Audio Reference Design

Firmware
========

6v00:    
    - ADDED:      Support for SU1 (Via SU1 Core Board and Audio Slice) - see app_usb_aud_skc_su1
    - ADDED:      Design moved to new build system
    - ADDED:      Optional support for USB test modes
    - ADDED:      Optional support for iOS devices (available to MFI licensees only)
    - CHANGE:     Now uses latest XUD API
    - CHANGE:     MIDI buffering simplified (using new XUD API) - no longer goes through decouple thread
    - CHANGE:     Now uses sc_i2c from www.github.com/xcore/sc_i2c 
    - CHANGE:     Previous default serial string of "0000" removed. No serial string now reported.
    - CHANGE:     Master volume update optimised slightly (updateMasteVol in audiorequests.xc)
    - CHANGE:     Master volume control disabled in Audio Class 1.0 mode to solve various issues in Windows
    - RESOLVED:   (Minor) Fixed issue where buffering can lock up on sample frequency change if in overflow (#10897)
    - RESOLVED:   (Minor) XN files updated to avoid deprecation warnings from tools

(Note: USB Audio version numbers unified across all products at this point)

Previous L1 Firmware Releases
=============================

3v30:
    - ADDED:      Added support for protocol Stall for un-recognised requests to Endpoint 0.
                  BOS Descriptor test in latest version of USB CV test now passes.
    - RESOLVED:   (Major) Removed redundant delays in DFU image download.  This aids Windows DFU reliability. 
    - RESOLVED:   (Minor) DFU Run-time descriptors updated from DFU 1.0 to DFU 1.1 spec.  This allows USB CV test pass.
    - RESOLVED:   (Minor) MIDI string descriptors added to string table.
    - RESOLVED:   (Minor) bInterval value for feedback endpoint modified to be more compatible with Microsoft OSs 
                  (support for iso endpoints with bInterval > 8 microframes).  This aids compatibility with 3rd party 
                  drivers for USB 3.0 controllers.
    - RESOLVED:   (Minor) Fixed build failure when NUM_USB_CHAN_IN/NUM_USB_CHAN_OUT defined as 0. Previous INPUT/OUTPUT 
                  defines now based on NUM_USB_CHAN_XXX defines. 
    - RESOLVED:   (Minor) Removed redundant calls to assert() to free memory. 


3v20:
    - RESOLVED:   (Major) Fixed reset reliability for self-powered devices.  This was due to an issue with 
                  XUD/Endpoint synchronisation during communication of RESET bus state over channels.
                  Bus powered devices should not be effected due to power up on every plug event.  
                  Note: Changes limited to XUD library only.

3v11:
    - RESOLVED    (Major) Removed size in re-interpret cast of DFU data buffer (unsigned to unsigned char). This
                  was due to a new optimisation in the 11.2 compiler which removes part of the DFU buffer (dfu.xc)
                  as it considers it un-used.  This causes the DFU download request to fail due to stack corruption.
3v10: 
    - ADDED:      Re-added LEDA "Valid Host" functionality using VendorHostActive() call. This functionality
                  missing since 3v00.  Note LED now indicated "Valid Host" rather than "Suspend" condition
    - RESOLVED:   (Major) Fixed issue when sharing bus with other devices especially high throughput bulk devices 
                  (e.g. hard disk drive). This is issue typically caused SOFs to missed by the device 
                  resulting in incorrect feedback calculation and ultimately audio glitching.  Note: this effects
                  XUD library only.
    - RESOLVED:   (Major) Intermittent issues with device chirp could lead to a bad packet on bus and device not
                  being properly detected as high-speed.  This was due to opmode of transceiver sometimes 
                  not being set before chirp. Note: this effects XUD library only.
    - RESOLVED:   (Minor) Intermittent USB CV Test fails with some hub models. Caused by test issuing suspend
                  during resume signalling. Note: this effects XUD library only                
    - RESOLVED:   (Minor) bMaxPower now set to 10mA (was 500mA) since this is a self-powered design (see 
                  SELF_POWERED define)
    - RESOLVED:   (Minor) Added code to deal with malformed audio packets from a misbehaving driver.
                  Previously this could result in the device audio buffering raising an exception.
    - RESOLVED:   (Minor) First packet of audio IN stream now correct to current sample-rate.  
                  Previously first packet was of length relating to previous sample rate.
    - RESOLVED:   (Minor) MIDI OUT buffering code simplified.  Now a single buffer used instead 
                  of previous circular buffer.
    - RESOLVED:   (Minor) Audio OUT stream buffer pre-fill level increased.
    - RESOLVED:   (Minor) Under stressed conditions the Windows built in Audio Class 1.0 driver (usbaudio.sys)
                  may issue invalid sample frequencies (e.g. 48001Hz) leading to an unresponsive device. 
                  Additional checks added to cope with this.

3v02:
    - RESOLVED:   Windows build issue (#9681)

3v01:
    - RESOLVED:   Version number reported as 0x0200, not 0x0300 (#9676)

3v00:
    - ADDED:      Added support to allow easy addition of custom audio requests
    - ADDED:      Optional "Host Active" function calls 
    - RESOLVED:   Single sample delay between ADC L/R channels resolved (#8783)
    - RESOLVED:   Use of MIDI cable numbers now compliant to specification (#8892)
    - RESOLVED:   Improved USB interoperability and device performance when connected through chained hubs 
    - RESOLVED:   S/PDIF Tx channel status bits (32-41) added for improved compliance
    - RESOLVED:   Increased robustness of high-speed reset recovery

2v00:
	- Buffering re-factoring
	- Addition of MIDI 

1v70:
	- Buffering fixes for non-intel USB chipsets

1v70:
    - Modifications for XMOS 10.4 tools release
    - Added USB Compliance Test Mode support
    - Added 88.2kHz sample frequency support for Audio Class 1.0
    - Various fixes for USB Compliance Command Verifier 

1v64: 
    - Thesycon Windows Driver DFU support added
    - LSB inprecision at 0dB volume fixed
    - DFU now supports custom flash parts

1v50:
    - Audio Class 1.0 available using build option, runs at full-speed
    - Device falls back to Audio Class 1.0 when connected via a full-speed hub
    - DFU functionality added

1v45:
    - Suspend/Resume supported.  LED A indicates suspend condition
    - LED B now indicates presence of audio stream
    - Code refactor for easy user customisation

1v30:
    - Fixed feedback issue in 1v2 release of USB library xud.a (used 3-byte feedback)
    
1v20:
    - Device now enumerates correctly on Windows
    
1v10:
    - Device enumerates as 24bit (previously 32bit)
    - Bit errors at 96kHz and 192kHz resolved
    - S/PDIF output functionality added
    - 88.2KHz analog in/out and S/PDIF output added
    - 176.4KHz analog in/out added.  S/PDIF not supported at this frequency because it requires 2xMCLK. 
	  Board has 11.2896Mhz, and would require 22.579Mhz.
  
1v00:
    - Initial release


Hardware
========

1v2: 
    - Explicit power supply sequencing
    - Power-on reset modified to include TRST_N

1v1:
    - Master clock re-routed to reduce cross-talk

1v0:
    - Initial Version


Previous L2 Firmware Releases
=============================

5v30
    - ADDED:      Added support for protocol Stall for un-recognised requests to Endpoint 0.
                  BOS Descriptor test in latest version of USB CV test now passes.
    - RESOLVED:   (Major) Removed redundant delays in DFU image download.  This aids Windows DFU reliability. 
    - RESOLVED:   (Minor) DFU Run-time descriptors updated from DFU 1.0 to DFU 1.1 spec.  This allows USB CV test pass.
    - RESOLVED:   (Minor) MIDI string descriptors added to string table.
    - RESOLVED:   (Minor) bInterval value for feedback endpoint modified to be more compatible with Microsoft OSs 
                  (support for iso endpoints with bInterval > 8 microframes).  This aids compatibility with 3rd party 
                  drivers for USB 3.0 controllers.
    - RESOLVED:   (Minor) Fixed build failure when NUM_USB_CHAN_IN/NUM_USB_CHAN_OUT defined as 0. Previous INPUT/OUTPUT 
                  defines now based on NUM_USB_CHAN_XXX defines. 
    - RESOLVED:   (Minor) Fixed build failure when MIXER defined as 0.
    - RESOLVED:   (Minor) MAX_MIX_OUTPUTS define now effects device descriptors.  Previously only effected mixer 
                  processing.
    - RESOLVED:   (Minor) Removed redundant calls to assert() to free memory. 

5v20:
    - RESOLVED:   (Major) Fixed reset reliability for self-powered devices.  This was due to an issue with 
                  XUD/Endpoint synchronisation during communication of RESET bus state over channels.
                  Bus powered devices should not be effected due to power up on every plug event.  
                  Note: Changes limited to XUD library only.

5v11:
    - RESOLVED:   (Major) Removed size in re-interpret cast of DFU data buffer (unsigned to unsigned char). This
                  was due to a new optimisation in the 11.2 compiler which removes part of the DFU buffer (dfu.xc)
                  as it considers it un-used.  This causes the DFU download request to fail due to stack corruption.

5v10:
    - RESOLVED:   (Major) Fixed issue when sharing bus with other devices especially high throughput bulk devices 
                  (e.g. hard disk drive). This is issue typically caused SOFs to missed by the device 
                  resulting in incorrect feedback calculation and ultimately audio glitching.  Note: Changes
                  limited to XUD library only.
    - RESOLVED:   (Major) Intermittent issues with device chirp could lead to a bad packet on bus and device not
                  being properly detected as high-speed.  This was due to opmode of transceiver sometimes 
                  not being set before chirp. Note: Changes limited to XUD library only.
    - RESOLVED:   (Minor) Intermittent USB CV Test fails with some hub models. Caused by test issuing suspend
                  during resume signalling. Note: Changes limited to XUD library only.               
    - RESOLVED:   (Minor) bMaxPower now set to 10mA (was 500mA) since this is a self-powered design (see 
                  SELF_POWERED define)
    - RESOLVED:   (Minor) Added code to deal with malformed audio packets from a misbehaving driver.
                  Previously this could result in the device audio buffering raising an exception.
    - RESOLVED:   (Minor) First packet of audio IN stream now correct to current samplerate.  
                  Previously first packet was of length relating to previous sample rate.
    - RESOLVED:   (Minor) MIDI OUT buffering code simplified.  Now a single buffer used instead of 
                  previous circular buffer.
    - RESOLVED:   (Minor) Audio OUT stream buffer pre-fill level increased.


5v00: 
    - ADDED:      Added support to allow easy addition of custom audio requests
    - ADDED:      Optional level meter processing added to mixer
    - ADDED:      Volume control locations customisable (before/after mix etc)
    - ADDED:      Mixer inputs are now runtime configurable (includes an "off" setting)
    - ADDED:      Mixer/routing topology now compliant to Audio Class 2.0 specification
    - ADDED:      Host mixer application updated for new topology and routing (and re-ported to Windows/Thesycon)
    - ADDED:      Saturation added to mixer arithmetic
    - ADDED:      Optional "Host Active" function calls (Example usage included)
    - ADDED:      Optional "Clock Validity" function calls (Example usage included)
    - RESOLVED:   Single sample delay between ADC L/R channels resolved (#8783)
    - RESOLVED:   Issue where external PLL could sometimes be unlocked due to cable unplug (#9179) 
    - RESOLVED:   Use of MIDI cable numbers now compliant to specification (#8892)
    - RESOLVED:   Improved USB interoperability and device performance when connected through chained hubs 
    - RESOLVED:   S/PDIF Tx channel status bits (32-41) added for improved compliance
    - RESOLVED:   Various performance optimisations added to mixer code
    - RESOLVED:   Increased robustness of high-speed reset recovery

4v00:
    - ADDED:      Addition of ADAT RX
    - ADDED:      Design can now cope with variable channel numbers set by the host (via Alternate Interfaces)
    - ADDED:      Fix to mixer volume range (range and resolution now definable in customdefines.h) (#9051)   

3v00:
    - ADDED:      Addition of mixer
    - ADDED:      Example host mixer application to package.  Uses Lib USB for OSX/Linux, Thesycon for Windows
    - RESOLVED:   Fixed internal clock mode jitter on reference to fractional-n

2v00:
    - ADDED:      Addition of S/PDIF Rx functionality and associated clocking functionality
    - ADDED:      Addition of Interrupt endpoint (interrupts on clock sources)
    - RESOLVED:   String descriptors added for input channels
    - RESOLVED:   Full-speed fall-back descriptors corrected for compliance

1v00:
    - ADDED:      Addition of MIDI input/output functionality
    - ADDED:      Addition of DFU functionality
    - RESOLVED:   Descriptor fixes for Windows (Thesycon) driver

0v52:
    - ADDED:      Addition of support for CODEC in master mode (see CODEC_SLAVE define)

0v51:
    - ADDED:      BCLK == MCLK now supported (i..e 192kHz from 12.288MHz)
    - ADDED:      MCLK defines now propagate to feedback calculation and CODEC configuration
    - RESOLVED:   XN file update for proper xflash operation

0v50:
    - Initial Alpha release
    - 10 channel input/output (8 chan DAC, 6 chan ADC, 2 chan S/PDIF tx)
    - Master/channel volume/mute controls
    

Hardware
========

1v1:
    - Initial production

1v0:
    - Pre-production


