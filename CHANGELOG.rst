sw_usb_audio Change Log
=======================

6.6.2
-----
    - CHANGE:     "Output" and "Input" no longer appended to Audio string descriptors

6.6.1
-----
    - ADDED:      DFU documentation
    - ADDED:      XUD_PWR_CFG define
    - CHANGE:     DSD ports now only enabled once to avoid potential lock up on DSD->PCM mode change
                  due to un-driven line floating high. ConfigAudioPortsWrapper() also simplified.
    - RESOLVED:   Makefile issue for 2ioxx config in app_usb_aud_skc_su1

  * Changes to dependencies:

    - sc_xud: 2.1.1rc0 -> 2.2.1rc0

      + RESOLVED:   Slight optimisations (long jumps replaced with short) to aid inter-packet gaps.
      + CHANGE:     Timer usage optimisation - usage reduced by one.
      + CHANGE:     OTG Flags register explicitly cleared at start up - useful if previously running

    - sc_usb_audio: 6.6.0rc2 -> 6.6.2rc0

      + see sw_usb_audio for changelog

    - sc_usb_device: 1.3.0rc0 -> 1.3.2rc0

      + sc_xud: 2.1.1rc0 -> 2.2.0rc0
      + CHANGE:     Timer usage optimisation - usage reduced by one.
      + CHANGE:     OTG Flags register explicitly cleared at start up - useful if previously running

6.6.0
-----
    - ADDED:      Added app_usb_aud_skc_u16_audio8 application for XP-SKC-U16 with XA-SK-AUDIO8
    - CHANGE:     Support for XA-SK-USB-BLC 1V2 USB slice in app_usb_aud_xk_u8_2c and
                  app_usb_aud_skc_u16 (1V1 slices will not operate correctly without software
                  modification)
    - CHANGE:     Removed app_usb_aud_su1
    - CHANGE:     Endpoint 0 code updated to support new XUD test-mode enable API
    - CHANGE:     Macs operation for volume processing in mixer core now retains lower bits when
                  device configured to use either 32bit samples or Native DSD.
    - RESOLVED:   (Minor) DFU_FLASH_DEVICE define corrected in app_usb_aud_skc_u16. Previously an
                  incorrect SPI spec was defined causing DFU to fail for this example application.
    - RESOLVED:   (Minor) HID descriptor properly defined when HID_CONTROLS enabled

  * Changes to dependencies:

    - sc_xud: 2.0.1rc3 -> 2.1.1rc0

      + ADDED:      Warning emitted when number of cores is greater than 6
      + CHANGE:     XUD no longer takes a additional chanend parameter for enabling USB test-modes.

    - sc_usb_audio: 6.5.1rc4 -> 6.6.0rc2

      + see sw_usb_audio for changelog

    - sc_usb_device: 1.2.2rc4 -> 1.3.0rc0

      + CHANGE:  Required updates for XUD API change relating to USB test-mode-support

6.5.1
-----
    - ADDED:      Added USB Design Guide to this repo including major update (see /doc)
    - ADDED:      Added MIDI_RX_PORT_WIDTH define such that a 4-bit port can be used for MIDI Rx
    - CHANGE:     I2S data to clock edge setup time improvements when BCLK = MCLK (particularly
                  when running at 384kHz with a 24.576MHz master-clock)
    - CHANGE:     String table rationalisation (now based on a structure rather than a global array)
    - CHANGE:     Channel strings now set at build-time (rather than run-time) avoiding the use
                  of memcpy
    - CHANGE:     Re-added c_aud_cfg channel (guarded by AUDIO_CFG_CHAN) allowing easy communication
                  of audio hardware config to a remote core
    - CHANGE:     Channel strings now labeled "Analogue X, SPDIF Y" if S/PDIF and Analogue channels
                  overlap (previously Analogue naming took precedence)
    - CHANGE:     Stream sample resolution now passed though to audio I/O core - previously only the
                  buffering code was notified. AudioHwConfig() now takes parameters for sample
                  resolution for DAC and ADC
    - CHANGE:     Endpoint0 core only sends out notifications of stream format change on stream start
                  event if there is an actual change in format (e.g. 16bit to 24bit or PCM to DSD).
                  This avoids unnecessary audio I/O restarts and reconfiguration of external audio
                  hardware (via AudioHwConfig())
    - CHANGE:     All occurances of historical INPUT and OUTPUT defines now removed. NUM_USB_CHAN_IN
                  and NUM_USB_CHAN_OUT now used throughout the codebase.
    - RESOLVED:   (Minor) USB test mode requests re-enabled - previously was guarded by
                  TEST_MODE_SUPPORT in module_usb_device (#15385)
    - RESOLVED:   (Minor) Audio Class 1.0 sample frequency list now respects MAX_FREQ (previously
                  based on OUTPUT and INPUT defines) (#15417)
    - RESOLVED:   (Minor) Audio Class 1.0 mute control SET requests stalled due to incorrect data
                  length check (#15419)
    - RESOLVED    (Minor) DFU Upload request now functional (Returns current upgrade image to host)
                  (#151571)

  * Changes to dependencies:

    - sc_spdif: 1.3.1beta3 -> 1.3.2rc2


    - sc_i2c: 2.4.0beta1 -> 2.4.1rc1
.
      + module_i2c_simple header-file comments updated to correctly reflect API

    - sc_usb_audio: 6.5.0beta2 -> 6.5.1rc4

      + see sw_usb_audio for changelog

    - sc_usb_device: 1.1.0beta0 -> 1.2.2rc4

      + sc_util: 1.0.3rc0 -> 1.0.4rc0
      + module_logging now compiled at -Os
      + debug_printf in module_logging uses a buffer to deliver messages unfragmented
      + Fix thread local storage calculation bug in libtrycatch
      + Fix debug_printf itoa to work for unsigned values > 0x80000000

    - sc_util: 1.0.3rc0 -> 1.0.4rc0

      + module_logging now compiled at -Os
      + debug_printf in module_logging uses a buffer to deliver messages unfragmented
      + Fix thread local storage calculation bug in libtrycatch
      + Fix debug_printf itoa to work for unsigned values > 0x80000000

    - sc_xud: 2.0.0beta1 -> 2.0.1rc3

      + RESOLVED:   (Minor) Error when building module_xud in xTimeComposer due to invalid project

6.5.0
-----
    - CHANGE:     USB Test mode support enabled by default (required for compliance testing)
    - CHANGE:     Default full-speed behaviour is now Audio Class 2, previously was a null device
    - CHANGE:     Various changes to use XUD_Result_t returned from XUD functions
    - CHANGE:     All remaining references to ARCH_x defines removed. XUD_SERIES_SUPPORT should
                  now be used (#15270)
    - CHANGE:     Added IAP_TILE and MIDI_TILE defines (default to AUDIO_IO_TILE) (#15271)
    - CHANGE:     Multiple output stream formats now supported. See OUTPUT_FORMAT_COUNT and
                  various _STREAM_FORMAT_OUTPUT_ defines. This allows dynamically selectable streaming
                  interfaces with different formats e.g. sub-slot size, resolution etc. 16bit and
                  24bit enabled by default
    - CHANGE:     Audio buffering code now handles different slot size for input/output streams
    - CHANGE:     Endpoint 0 code now in standard C (rather than XC) to allow better use of packed
                  structures for descriptors
    - CHANGE:     Use of structures/enums/headers in module_usb_shared to give more modular Audio
                  Class 2.0 descriptors that can be more easily modified at run-time
    - CHANGE:     16bit audio buffer packing/unpacking optimised
    - RESOLVED:   (Minor) All access to port32A now guarded by locks in app_usb_aud_xk_u8_2c
    - RESOLVED:   (Minor) iAP interface string index in descriptors when MIXER enabled (#15257)
    - RESOLVED:   (Minor) First feedback packet could be the wrong size (3 vs 4 byte) after a bus-
                  speed change. usb_buffer() core now explicitly re-sizes initial feedback packet
                  on stream-start based on bus-speed
    - RESOLVED:   (Minor) Preprocessor error when AUDIO_CLASS_FALLBACK enabled and FULL_SPEED_AUDIO_2
                  not defined. FULL_SPEED_AUDIO_2 now only enabled by default if AUDIO_CLASS_FALLBACK
                  is not enabled (#15272)
    - RESOLVED:   (Minor) XUD_STATUS_ENABLED set for iAP IN endpoints (and disabled for OUT
                  endpoint) to avoid potential stale buffer being transmitted after bus-reset.

6.4.1
-----
    - RESOLVED:   (Minor) MIDI on single-tile L series devices now functional. CLKBLK_REF no longer used
                  for MIDI when running on the same tile as XUD_Manager()

6.4.0
-----
    - ADDED:      XK-USB-AUDIO-U8-2C mute output driven high when audiostream not active (app_usb_aud_xk_u8_2c)
    - CHANGE:     MIDI ports no longer passed to MFi specific functions
    - CHANGE:     Audio delivery core no longer waits for AUDIO_PLL_LOCK_DELAY after calling AudioHwConfig()
                  and running audio interfaces. It should be ensured that AudioHwConfig() implementation
                  should handle any delays required for stable MCLK as required by the clocking hardware.
    - CHANGE:     Delay to allow USB feedback to stabilise after sample-rate change now based on USB bus
                  speed. This allows faster rate change at high-speed.
    - CHANGE:     FL_DEVICE_ flash spec macros (from flash.h) used for DFU_FLASH_DEVICE define where appropriate
                  rather than defining the spec manually
    - RESOLVED:   (Major) Broken (noisy) playback in DSD native mode (introduced in 6.3.2). Caused by 24bit
                  (over 32bit) volume processing when DSD enabled - DSD bits are lost. 24bit volume control
                  now guarded by NATIVE_DSD define (#15200)
    - RESOLVED:   (Minor) Default for SPDIF define set to 1 in app_usb_aud_l1 customdefines.h.
                  Previously SPDIF not properly enabled in binaries (#15129)
    - RESOLVED:   (Minor) All remaining references to stdcore[] replaced with tile[] (#15122)
    - RESOLVED:   (Minor) Removed hostactive.xc and audiostream.xc from app_usb_aud_skc_u16 such
                  that default implementations are used (hostactive.xc was using an invalid port) (#15118)
    - RESOLVED:   (Minor) The next 44.1 based freq above MAX_FREQ was reported by
                  GetRange(SamplingFrequency) when MAX_FREQ = MIN_FREQ (and MAX_FREQ was 48k based) (#15127)
    - RESOLVED:   (Minor) MIDI input events no longer intermittently dropped under heavy output traffic
                  (Typically SysEx) from USB host - MIDI Rx port now buffered (#14224)
    - RESOLVED:   (Minor) Fixed port mapping in app_usb_aud_skc_u16 XN file (#15124)
    - RESOLVED:   (Minor) DEFAULT_FREQ was assumed to be a multiple of 48k during initial calculation
                  of g_SampFreqMultiplier (#15141)
    - RESOLVED:   (Minor) SPDIF not properly enabled in any build of app_usb_aud_l1 (SPDIF define set to
                  0 in customdefines.h) (#15102)
    - RESOLVED:   (Minor) DFU enabled by default in app_usb_aud_l2 (#15153)
    - RESOLVED:   (Minor) Build issue when NUM_USB_CHAN_IN or NUM_USB_CHAN_OUT set to 0 and MIXER set to 1 (#15096)
    - RESOLVED:   (Minor) Build issue when CODEC_MASTER set (#15162)
    - RESOLVED:   (Minor) DSD mute pattern output when invalid DSD frequency selected in Native DSD mode. Previously
                  0 was driven resulting in pop noises on the analague output when switching between DSD/PCM (#14769)
    - RESOLVED:   (Minor) Build error when OUT_VOLUME_IN_MIXER was set to 0 (#10692)
    - RESOLVED:   (Minor) LR channel swap issue in CS42448 CODEC by more closely matching recommended
                  power up sequence (app_usb_aud_l2) (#15189)
    - RESOLVED:   (Minor) Improved the robustness of ADC I2S data port init when MASTER_CODEC defined (#15203)
    - RESOLVED:   (Minor) Channel counts in Audio 2 descriptors now modified based on bus-speed. Input stream
                  format also modified (previously only output was) (#15202)
    - RESOLVED:   (Minor) Full-speed Audio Class 2.0 sample-rate list properly restricted based on if input
                  /output are enabled (#15210)
    - RESOLVED:   (Minor) AUDIO_CLASS_FALLBACK no longer required to be defined when AUDIO_CLASS set to 1 (#13302)

  * Changes to dependencies:

    - sc_usb_device: 1.0.3beta0 -> 1.0.4beta5

      + CHANGE:     devDesc_hs and cfgDesc_hs params to USB_StandardRequests() now nullable (useful for full-speed only devices)
      + CHANGE:     Nullable descriptor array parameters to USB_StandardRequests() changed from ?array[] to (?&array)[] due to

    - sc_xud: 1.0.2alpha1 -> 1.0.3beta1

      + RESOLVED:   (Minor) ULPI data-lines driven hard low and XMOS pull-up on STP line disabled
      + RESOLVED:   (Minor) Fixes to improve memory usage such as adding missing resource usage
      + RESOLVED:   (Minor) Moved to using supplied tools support for communicating with the USB tile

    - sc_usb: 1.0.1beta1 -> 1.0.2beta1

      + ADDED:   USB_BMREQ_D2H_VENDOR_DEV and USB_BMREQ_D2H_VENDOR_DEV defines for vendor device requests

6.3.2
-----
    - ADDED:      SAMPLE_SUBSLOT_SIZE_HS/SAMPLE_SUBSLOT_SIZE_FS defines (default 4/3 bytes)
    - ADDED:      SAMPLE_BIT_RESOLUTION_HS/SAMPLE_BIT_RESOLUTION_FS defines (default 24/24 bytes)
    - CHANGE:     PIDs in app_usb_aud_xk_2c updated (previously shared with app_usb_aud_skc_su1). Requires Thesycon 2.15 or later
    - RESOLVED:   (Minor) Fixed maxPacketSize for audio input endpoint (was hard-coded to 1024)

  * Changes to dependencies:

    - sc_xud: 1.0.1beta3 -> 1.0.2alpha1

      + ADDED:        Re-instated support for G devices (xud_g library)

    - sc_usb_device: 1.0.2beta0 -> 1.0.3beta0

6.3.1
-----
    - ADDED:      Reinstated application for XR-USB-AUDIO-2.0-MC board (app_usb_aud_l2)
    - ADDED:      Support for operation with Apple devices (MFI licensees only - please contact XMOS)
    - ADDED:      USER_MAIN_DECLARATIONS and USER_MAIN_CORES defines in main for easy addition of custom cores
    - CHANGE:     Access to shared GPIO port (typically 32A) in app code now guarded with a lock for safety
    - CHANGE:     Re-organised main() to call two functions with the aim to improve readability
    - CHANGE:     Event queue logic in MIDI now in XC module-queue such that it can be inlined (code-size saving)
    - CHANGE:     Various functions now marked static to encourage inlining, saving around 200 bytes of code-size
    - CHANGE:     Removed redundant MIDI buffering code from previous buffering scheme
    - CHANGE:     Some tidy of String descriptors table and related defines

  * Changes to dependencies:

    - sc_i2c: 2.2.1rc0 -> 2.3.0beta1

      + module_i2c_simple fixed to ACK correctly during multi-byte reads (all but the final byte will be now be ACKd)
      + module_i2c_simple can now be built with support to send repeated starts and retry reads and writes NACKd by slave
      + module_i2c_shared added to allow multiple logical cores to safely share a single I2C bus
      + Removed readreg() function from single_port module since it was not safe

    - sc_spdif: 1.3.0rc4 -> 1.3.1beta2

      + Added .type and .size directives to SpdifReceive. This is required for the function to show up in xTIMEcomposer binary viewer

6.3.0
-----
    - ADDED:      Application for XP-SKC-U16 board with XA-SK-AUDIO slice (app_usb_aud_xkc_u16)
    - CHANGE:     Moved to XMOS toolchain version 13

6.2.1
-----
    - ADDED:      DEFAULT_MCLK_FREQ define added
    - RESOLVED:   Native DSD now easily disabled whilst keeping DoP mode enabled (setting NATIVE_DSD to 0 with DSD_CHANS_DAC > 0)
    - RESOLVED:   Device could become unresponsive if the host outputs a stream with an invalid DoP frequency (#14938)

6.2.0
-----
    - ADDED:      Application for XK-USB-AUDIO-U8-2C board
    - ADDED:      PRODUCT_STR define for Product Strings
    - ADDED:      Added DSD over PCM (DoP) mode
    - ADDED:      Added Native DSD (Driver support required)
    - ADDED:      Added optional channel for audio buffing control, this can reduce power consumption
    - ADDED:      The device can run in Audio Class 2.0 when connected to a full-speed hub using the FULL_SPEED_AUDIO_2 define
    - ADDED:      MIN_FREQ configuration define for setting minimum sample rate of device (previously assumed 44.1)
    - CHANGE:     Endpoint0 code migrated to use new module_usb_device shared module
    - CHANGE:     Device reboot code (for DFU) made more generic for multi-tile systems
    - CHANGE:     DFU code now erases all upgrade images found, rather than just the first one
    - CHANGE:     ports.h file no longer required.  Please declare custom ports in your own files
    - CHANGE:     Define based warnings in devicedefines.h moved to warnings.xc to avoid multiple warnings being issued
    - RESOLVED:   (Major) ADC port initialization did not operate as expected at 384kHz
    - RESOLVED:   (Major) Resolved a compatibility issue with streaming on Intel USB 3.0 xHCI host controller
    - RESOLVED:   (Major) Added defence against malformed Audio Class 1.0 packets as experienced on some Win 8.0 hosts. Previously this would cause an exception (Issue fixed in Win 8.1)
    - RESOLVED:   (Minor)  maxPacketSize now reported based on device's read bandwidth requirements.  This allows the driver to reserve the proper bandwidth amount (previously bandwidth would have been wasted)
    - RESOLVED:   (Minor) Input channel strings used for output in one instance
    - RESOLVED:   (Minor) Volume multiplication now compatible with 32bit samples. Previously assumed 24bit samples and would truncate bottom 3 bits
    - RESOLVED:   (Minor) Fixed issue with SE0_NAK test mode (as required for device receiver sensitivity USB-IF compliance test
    - RESOLVED:   (Minor) Fixed issue with packet parameters compliance test
    - RESOLVED:   (Minor) Added bounds checking to string requests. Previously an exception was raised if an invalid String was requested

6.1.0
-----
    - RESOLVED:   Resolved issue with DFU caused by SU1 ADC usage causing issues with soft reboot
    - ADDED:      Added ability for channel count changes between UAC1 and UAC2 modes
    - ADDED:      Support for iOS authentication (MFI licencees only - please contact XMOS)

6.0.1
-----
    - CHANGE:     Removed support for early engineering sample U-series devices

6.0.0
-----
    - ADDED:      Support for SU1 (Via SU1 Core Board and Audio Slice) - see app_usb_aud_skc_su1
    - ADDED:      Design moved to new build system
    - ADDED:      Optional support for USB test modes
    - ADDED:      Optional HID endpoint for audio controls and example usages
    - ADDED:      Multiple build configurations for supported device configurations
    - CHANGE:     Now uses latest XUD API
    - CHANGE:     MIDI buffering simplified (using new XUD API) - no longer goes through decouple thread
    - CHANGE:     Now uses sc_i2c from www.github.com/xcore/sc_i2c
    - CHANGE:     Previous default serial string of "0000" removed. No serial string now reported.
    - CHANGE:     Master volume update optimised slightly (updateMasterVol in audiorequests.xc)
    - CHANGE:     Master volume control disabled in Audio Class 1.0 mode to solve various issues in Windows
    - CHANGE:     Audio Class 2.0 Status/Interrupt endpoint disabled by default (enabled when SPDIF/ADAT receive enabled)
    - CHANGE:     DFU/Flash code simplified
    - RESOLVED:   (Minor) Fixed issue where buffering can lock up on sample frequency change if in overflow (#10897)
    - RESOLVED:   (Minor) XN files updated to avoid deprecation warnings from tools
    - RESOLVED:   (Major) Fixed issue where installation of the first upgrade image is successful but subsequent upgrades fail (Design Advisory X2035A)

(Note: USB Audio version numbers unified across all products at this point)

Previous L1 Firmware Releases

3.3.0
-----
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


3.2.0
-----
    - RESOLVED:   (Major) Fixed reset reliability for self-powered devices.  This was due to an issue with
                  XUD/Endpoint synchronisation during communication of RESET bus state over channels.
                  Bus powered devices should not be effected due to power up on every plug event.
                  Note: Changes limited to XUD library only.

3.1.1
-----
    - RESOLVED    (Major) Removed size in re-interpret cast of DFU data buffer (unsigned to unsigned char). This
                  was due to a new optimisation in the 11.2 compiler which removes part of the DFU buffer (dfu.xc)
                  as it considers it un-used.  This causes the DFU download request to fail due to stack corruption.
3.1.0
-----
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

3.0.2
-----
    - RESOLVED:   Windows build issue (#9681)

3.0.1
-----
    - RESOLVED:   Version number reported as 0x0200, not 0x0300 (#9676)

3.0.0
-----
    - ADDED:      Added support to allow easy addition of custom audio requests
    - ADDED:      Optional "Host Active" function calls
    - RESOLVED:   Single sample delay between ADC L/R channels resolved (#8783)
    - RESOLVED:   Use of MIDI cable numbers now compliant to specification (#8892)
    - RESOLVED:   Improved USB interoperability and device performance when connected through chained hubs
    - RESOLVED:   S/PDIF Tx channel status bits (32-41) added for improved compliance
    - RESOLVED:   Increased robustness of high-speed reset recovery

2.0.0
-----
	- Buffering re-factoring
	- Addition of MIDI

1.7.0
-----
	- Buffering fixes for non-intel USB chipsets

1.7.0
-----
    - Modifications for XMOS 10.4 tools release
    - Added USB Compliance Test Mode support
    - Added 88.2kHz sample frequency support for Audio Class 1.0
    - Various fixes for USB Compliance Command Verifier

1.6.4
-----
    - Thesycon Windows Driver DFU support added
    - LSB inprecision at 0dB volume fixed
    - DFU now supports custom flash parts

1.5.0
-----
    - Audio Class 1.0 available using build option, runs at full-speed
    - Device falls back to Audio Class 1.0 when connected via a full-speed hub
    - DFU functionality added

1.4.5
-----
    - Suspend/Resume supported.  LED A indicates suspend condition
    - LED B now indicates presence of audio stream
    - Code refactor for easy user customisation

1.3.0
-----
    - Fixed feedback issue in 1v2 release of USB library xud.a (used 3-byte feedback)

1.2.0
-----
    - Device now enumerates correctly on Windows

1.1.0
-----
    - Device enumerates as 24bit (previously 32bit)
    - Bit errors at 96kHz and 192kHz resolved
    - S/PDIF output functionality added
    - 88.2KHz analog in/out and S/PDIF output added
    - 176.4KHz analog in/out added.  S/PDIF not supported at this frequency because it requires 2xMCLK.
	  Board has 11.2896Mhz, and would require 22.579Mhz.

1.0.0
-----
    - Initial release


L1 Hardware

1.2.0
-----
    - Explicit power supply sequencing
    - Power-on reset modified to include TRST_N

1.1.0
-----
    - Master clock re-routed to reduce cross-talk

1.0.0
-----
    - Initial Version


Previous L2 Firmware Releases

5.3.0
-----
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

5.2.0
-----
    - RESOLVED:   (Major) Fixed reset reliability for self-powered devices.  This was due to an issue with
                  XUD/Endpoint synchronisation during communication of RESET bus state over channels.
                  Bus powered devices should not be effected due to power up on every plug event.
                  Note: Changes limited to XUD library only.

5.1.1
-----
    - RESOLVED:   (Major) Removed size in re-interpret cast of DFU data buffer (unsigned to unsigned char). This
                  was due to a new optimisation in the 11.2 compiler which removes part of the DFU buffer (dfu.xc)
                  as it considers it un-used.  This causes the DFU download request to fail due to stack corruption.

5.1.0
-----
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


5.0.0
-----
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

4.0.0
-----
    - ADDED:      Addition of ADAT RX
    - ADDED:      Design can now cope with variable channel numbers set by the host (via Alternate Interfaces)
    - ADDED:      Fix to mixer volume range (range and resolution now definable in customdefines.h) (#9051)

3.0.0
-----
    - ADDED:      Addition of mixer
    - ADDED:      Example host mixer application to package.  Uses Lib USB for OSX/Linux, Thesycon for Windows
    - RESOLVED:   Fixed internal clock mode jitter on reference to fractional-n

2.0.0
-----
    - ADDED:      Addition of S/PDIF Rx functionality and associated clocking functionality
    - ADDED:      Addition of Interrupt endpoint (interrupts on clock sources)
    - RESOLVED:   String descriptors added for input channels
    - RESOLVED:   Full-speed fall-back descriptors corrected for compliance

1.0.0
-----
    - ADDED:      Addition of MIDI input/output functionality
    - ADDED:      Addition of DFU functionality
    - RESOLVED:   Descriptor fixes for Windows (Thesycon) driver

0.5.2
-----
    - ADDED:      Addition of support for CODEC in master mode (see CODEC_SLAVE define)

0.5.1
-----
    - ADDED:      BCLK == MCLK now supported (i..e 192kHz from 12.288MHz)
    - ADDED:      MCLK defines now propagate to feedback calculation and CODEC configuration
    - RESOLVED:   XN file update for proper xflash operation

0.5.0
-----
    - Initial Alpha release
    - 10 channel input/output (8 chan DAC, 6 chan ADC, 2 chan S/PDIF tx)
    - Master/channel volume/mute controls


L2 Hardware

1.2.0
-----
    - Update for coax in, coax out cap & minor tidyup

1.1.0
-----
    - Initial production

1.0.0
-----
    - Pre-production


