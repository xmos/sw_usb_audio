sw_usb_audio Change Log
=======================

8.1.0
-----

  * ADDED:     2AMi18o18mssaax build config (MIDI, SPDIF Rx/Tx & ADAT Rx/Tx)
  * ADDED:     2AMi16o16xxxaax build config (ADAT Rx/Tx)
  * ADDED:     2AMi8o8mxxxxx build config (MIDI)
  * CHANGED:   Use lib_sw_pll code for configuring the application PLL
  * FIXED:     Use correct number of flash pages for XK-AUDIO-316-MC
  * FIXED:     Links to usb.org in documentation

  * Changes to dependencies:

    - lib_adat: 1.1.0 -> 1.2.0

      + CHANGED: example applications now run on xcore.ai hardware
      + CHANGED: example applications build using XCommon CMake

    - lib_sw_pll: 2.1.0 -> 2.2.0

      + FIXED: Enable PLL output after delay to allow it to settle
      + FIXED: Fixed frequency settings for 11,289,600Hz

    - lib_xua: 4.0.0 -> 4.1.0

      + ADDED:     MIDI unit and sub-system tests
      + CHANGED:   Only the minimum number of ADAT input formats are enabled
        based on the supported sample rates
      + CHANGED:   Enabling ADAT tx enables different channel count interface
        alts, based on sample rate
      + CHANGED:   Input audio buffer size and the exit condition underflow
        modified to to fix buffer underflow in some configurations
      + CHANGED:   CT_END token based handshake in MIDI channels transactions,
        reducing opportuninity for deadlock
      + FIXED:     Device fails to enumerate when ADAT and S/PDIF transmit are
        enabled
      + FIXED:     Update software PLL at the correct rate for ADAT S/MUX
      + FIXED:     Incorrect internal input EP count for input only devices
      + FIXED:     Samples transferred to ADAT tx too frequently in TDM mode
      + FIXED:     S/MUX not initialised to a value based on DEFAULT_FREQ in
        clockgen
      + FIXED:     Trap when moving to DSD mode on XS3A based devices

8.0.0
-----

  * ADDED:     Support for XCommon CMake build system
  * CHANGED:   Windows control app now take GUID via a -g option, accommodating
    latest Thesycon driver packages
  * CHANGED:   app_usb_aud_xk_316_mc defaults to using xcore.ai AppPLL for
    master clock generation when syncing to digital streams or in USB sync mode,
    rather than the external CS2100 device
  * CHANGED:   UserBufferManagmentInit() implementations updated to match API
    change in lib_xua (now takes a sample rate value)
  * CHANGED:   app_usb_aud_xk_316_mc: Improvements in interaction with on-board
    power control circuitry

  * Changes to dependencies:

    - lib_adat: 1.0.1 -> 1.1.0

      + ADDED: Support for XCommon CMake build system

    - lib_dsp: 6.2.1 -> 6.3.0

      + ADDED:   Support for XCommon CMake build system

    - lib_i2c: 6.1.1 -> 6.2.0

      + ADDED: Support for XCommon CMake build system
      + REMOVED: Unused dependency lib_logging

    - lib_i2s: 5.0.0 -> 5.1.0

      + ADDED: Support for XCommon CMake build system
      + RESOLVED: Added missing shutdown feature to i2s_frame_slave
      + FIXED: Allow input and output ports in the 4-bit port implementation to
        be nullable
      + FIXED: Behaviour of the restart_check() callback function in the example
        applications
      + REMOVED: Unused dependency lib_logging
      + ADDED: Frame synch error field in i2s_config_t for I2S slave

    - lib_locks: 2.1.0 -> 2.2.0

      + ADDED: Tests now run on xcore.ai as well as xcore-200
      + ADDED: Support for XCommon CMake build system

    - lib_logging: 3.1.1 -> 3.2.0

      + ADDED:   Support for XCommon CMake build system

    - lib_mic_array: 4.5.0 -> 4.6.0

      + ADDED: Support for XCommon CMake build system

    - lib_spdif: 5.0.1 -> 6.1.0

      + ADDED:     Support for XCommon CMake build system
      + ADDED:     Support for transmit at 32kHz
      + RESOLVED:  Coding optimisations not properly enabled in receiver
      + RESOLVED:  Receiver timing issues for sample rates greater than 96kHz
      + RESOLVED:  Failure to select correct receive sample rate when the sample
        rate of the incoming stream changes
      + ADDED:     Shutdown function for S/PDIF transmitter
      + CHANGED:   Receiver rearchitected for improved performance and jitter
        tolerance
      + CHANGED:   API function names updated for uniformity between rx and tx

    - lib_sw_pll: Added dependency 2.1.0

      + ADDED: Support for XCommon CMake build system
      + ADDED: Reset PI controller state API
      + ADDED: Fixed frequency (non phase-locked) clock PLL API
      + FIXED: Init resets PI controller state
      + FIXED: Now compiles from XC using XCommon
      + ADDED: Guard source code with __XS3A__ to allow library inclusion in
        non- xcore-ai projects
      + CHANGED: Reduce PLL initialisation stabilisation delay from 10 ms to 500
        us
      + ADDED: Split SDM init function to allow separation across tiles
      + FIXED: Use non-ACK write to PLL in Sigma Delta Modulator

    - lib_xassert: 4.1.0 -> 4.2.0

      + ADDED: Support for XCommon CMake build system

    - lib_xua: 3.5.1 -> 4.0.0

      + ADDED:     Support for XCommon CMake build system
      + FIXED:     Output volume control not enabled by default when MIXER
        disabled
      + FIXED:     Full 32bit result of volume processing not calculated when
        required
      + FIXED:     Input stream sending an erroneous zero-length packet when
        exiting underflow state
      + FIXED      Build failures when XUA_USB_EN = 0
      + FIXED:     Clock configuration issues when ADAT and S/PDIF receive are
        enabled (#352)
      + FIXED:     Repeated old S/PDIF and ADAT samples when entering underflow
        state
      + CHANGED:   QUAD_SPI_FLASH replaced by XUA_QUAD_SPI_FLASH (default: 1)
      + CHANGED:   UserBufferManagementInit() now takes a sample rate parameter
      + CHANGED:   xcore.ai targets use sigma-delta software PLL for clock
        recovery of digital Rx streams and synchronous USB audio by default
      + CHANGED:   Windows host mixer control application now requires driver
        GUID option

    - lib_xud: 2.2.3 -> 2.3.1

      + FIXED:     XS3A based devices not responding to IN packets in SE0_NAK
        test mode
      + ADDED:     XMOS proprietary test mode XMOS_IN_ADDR1
      + ADDED:     Support for XCommon CMake build system
      + CHANGE:    Removed definition and use of REF_CLK_FREQ in favour of
        PLATFORM_REFERENCE_MHZ from platform.h
      + FIXED:     Do not include implementations of inline functions when
        XUD_WEAK_API is set

7.3.1
-----

  * CHANGE:    app_usb_aud_xk_evk_xu316: Mixer disabled by default

  * Changes to dependencies:

    - lib_xua: 3.5.0 -> 3.5.1

      + FIXED:     Respect I2S_CHANS_PER_FRAME when calculating bit-clock rates

7.3.0
-----

  * CHANGE:    app_usb_aud_xk_316_mc: Respect XUA_I2S_N_BITS when configuring
    external audio hardware
  * ADDED:     Support for 12.288MHz 11.2896MHz to xcore.ai AppPLL master clock
    options
  * FIXED:     app_usb_aud_xk_316_mc: DAC settings not configured when sample
    rate is lower than 48kHz

  * Changes to dependencies:

    - lib_spdif: 4.2.1 -> 5.0.1

      + FIXED:     Reinstated graceful handling of bad sample-rate/master-clock
        pair
      + CHANGED:   Updated examples for new XK-AUDIO-316-MC board
      + CHANGED:   Updated transmit to simplified implementation (note, no
        longer supports XS1 based devices)
      + CHANGED:   Removed headers SpdifReceive.h and SpdifTransmit.h. Users
        should include spdif.h

    - lib_xua: 3.4.0 -> 3.5.0

      + ADDED:     Configurable word-length for I2S/TDM via XUA_I2S_N_BITS
      + ADDED:     Support for statically defined custom HID descriptor
      + CHANGED:   Rearranged main() such that adding custom code that uses
        lib_xud is possible
      + CHANGED:   bNumConfigurations changed from 2 to 1, removing a
        work-around to stop old Windows versions loading the composite driver
      + FIXED:     Memory corruption due to erroneous initialisation of mixer
        weights when not in use (#152)
      + FIXED:     UserHostActive() not being called as expected (#326)
      + FIXED:     Exception when entering DSD mode (#327)

    - lib_xud: 2.2.2 -> 2.2.3

      + FIXED:     XUD_UserSuspend() and XUD_UserResume() now properly marked as
        weak symbols (#374)
      + FIXED:     Incorrect time reference used during device attach process
        (#367)

7.2.0
-----

  * ADDED:     Driver information section to documentation
  * CHANGED:   AppPLL settings updated to reduce jitter (#112)
  * CHANGED:   app_usb_aud_316_mc: Improved DAC configuration sequencing
    following datasheet recommendations
  * CHANGED:   app_usb_aud_316_mc: Manual DAC setup rather than using
    auto-config to improve output quality (internal PLL no longer used)
  * FIXED:     app_usb_aud_316_mc: Intermittent output from DACs due to DAC
    auto-standby (#110)
  * FIXED:     app_usb_aud_216_mc: Define app defaults ahead of lib_xua defaults

  * Changes to dependencies:

    - lib_xua: 3.3.1 -> 3.4.0

      + ADDED:     Unit tests for mixer functionality
      + ADDED:     Host mixer control applications (for Win/macOS)
      + CHANGED:   Small tidies to mixer implementation
      + CHANGED:   Improved mixer control channel communication protocol to
        avoid deadlock situations
      + CHANGED:   By default, output volume processing occurs in mixer task, if
        present. Previously occurred in decouple task
      + CHANGED:   Some optimisations in sample transfer from decouple task
      + FIXED:     Exception on startup when USB input disabled
      + FIXED:     Full 32bit volume processing only applied when required
      + FIXED:     Setting OUT_VOLUME_AFTER_MIX to zero now has the expected
        effect

    - lib_xud: 2.2.1 -> 2.2.2

      + FIXED:     Syntax error when including xud.h from C
      + CHANGE:    Various API functions optionally marked as a weak symbol
        based on XUD_WEAK_API

7.1.0
-----

  * ADDED:     Build configs for synchronous mode (uses external CS2100 device)
  * ADDED:     app_usb_aud_xk_316_mc: Build configs for xCORE as I2S slave
  * CHANGED:   app_usb_aud_xk_316_mc: Core voltage reduced to 0.9v (was 0.922v)
  * CHANGED:   Separated build configs into build-tested, partially-tested and
    fully-tested
  * CHANGED:   Documentation updates (note, "Design Guide" now "User Guide")

  * Changes to dependencies:

    - lib_adat: 1.0.0 -> 1.0.1

      + Removed duplicate header file

    - lib_i2s: 4.3.0 -> 5.0.0

      + ADDED: Support for I2S data lengths less than 32 bit.
      + ADDED: Implementation allowing use of a 4-bit port for up to 4
        simultaneous streaming inputs or outputs.

    - lib_spdif: 4.1.0 -> 4.2.1

      + CHANGED:   Documentation updates
      + ADDED:     Shutdown function for S/PDIF receiver
      + CHANGED:   spdif_tx_example updated to use XK-AUDIO-216-MC

    - lib_xua: 3.2.0 -> 3.3.1

      + CHANGED:  Documentation updates
      + CHANGED:   Define ADAT_RX renamed to XUA_ADAT_RX_EN
      + CHANGED:   Define ADAT_TX renamed to XUA_ADAT_TX_EN
      + CHANGED:   Define SPDIF_RX renamed to XUA_SPDIF_RX_EN
      + CHANGED:   Define SELF_POWERED changed to XUA_POWERMODE and associated
        defines
      + CHANGED:   Drive strength of I2S clock lines upped to 8mA on xCORE.ai
      + CHANGED:   ADC datalines sampled on falling edge of clock in TDM mode
      + CHANGED:   Improved startup behaviour of TDM clocks
      + FIXED:     Intermittent underflow at MAX_FREQ on input stream start due
        to insufficient packet buffering
      + FIXED:     Decouple buffer accounting to avoid corruption of samples

    - lib_xud: 2.1.0 -> 2.2.1

      + FIXED:     Control endpoint ready flag not properly cleared on receipt
        of SETUP transaction (#356)
      + CHANGE:    Further API functions re-authored in C (were Assembly)
      + CHANGE:    Endpoints marked as Disabled now reply with STALL if the host
        attempts to access them, previously they would NAK (#342)
      + FIXED:     Exception if host accesses an endpoint that XUD believes to
        be not in use
      + FIXED:     Timeout event properly cleaned up after tx handshake received
        (#312)
      + FIXED:     A control endpoint will respect the halt condition for OUT
        transactions when marked ready to accept SETUP transactions (#339)
      + FIXED:     USB Disconnect on self-powered devices intermittently causing
        Iso EP's to be set to not-ready indefinitely (#351)

7.0.0
-----

  * ADDED:      Application for XK-AUDIO-316-MC hardware
  * ADDED:      Support for XTC Tools 15
  * CHANGED:    Removed apps for deprecated hardware
  * CHANGED:    HID implementation for MC audio board buttons
  * CHANGED:    Moved from using sc_ repos to lib_ repos (see dependency changes
    below)
  * FIXED:      Need to drive VBUS_OUT low on xCORE-200 MC AUDIO board (#17697)

  * Changes to dependencies:

    - lib_adat: Added dependency 1.0.0

      + Initial release

    - lib_device_control: Removed dependency

    - lib_dsp: Added dependency 6.2.1

      + CHANGED: Jenkinsfile used for CI

    - lib_i2c: Added dependency 6.1.1

      + RESOLVED: Fixed timing for repeated START condition

    - lib_i2s: Added dependency 4.3.0

      + CHANGED: Use XMOS Public Licence Version 1

    - lib_locks: Added dependency 2.1.0

      + CHANGED: Use XMOS Public Licence Version 1

    - lib_logging: 2.0.1 -> 3.1.1

      + CHANGED: Jenkinsfile used for CI
      + CHANGED: Use XMOS Public Licence Version 1
      + REMOVED: not necessary cpanfile
      + CHANGED: Pin Python package versions
      + CHANGED: Build files updated to support new "xcommon" behaviour in xwaf.
      + CHANGE:   Test runner script now terminates correctly on Windows
      + ADDED:    Now supports the %p format specifier
      + CHANGE:   Ignore the case of the format specifiers
      + CHANGE:   Ignore padding and alignment characters

    - lib_mic_array: 2.0.1 -> 4.5.0

      + REMOVED: Use of Brew for CI
      + CHANGED: XMOS Jenkins Shared Library version used in CI
      + CHANGED: XN files to support 15.x.x tools
      + CHANGED: Use XMOS Public Licence Version 1
      + FIXED: Compiler warnings when MIC_DUAL_ENABLED is not defined
      + CHANGED: Pin Python package versions
      + REMOVED: not necessary cpanfile
      + CHANGED: Jenkinsfile pinned to Jenkins shared library 0.10.0
      + CHANGED: Updated the minimum version of libraries this library depends
        upon.
      + ADDED support for global define to set single/dual output buffer for
        mic_dual
      + Added mic_dual, an optimised single core, 16kHz, two channel version
        (not compatible with async interface)
      + ADDED: Support for arbitrary frame sizes
      + ADDED: #defines for mic muting
      + ADDED: Non-blocking interface to decimators for 2 mic setup
      + CHANGED: Build files updated to support new "xcommon" behaviour in xwaf.
      + Added xwaf build system support
      + Cleaned up some of the code in the FIR designer.
      + Removed fixed gain in examples
      + Update VU meter example
      + Fix port types in examples
      + Set and inherit XCC_FLAGS rather than XCC_XC_FLAGS when building library
      + Updated lib_dsp dependancy from 3.0.0 to 4.0.0
      + Modified the FIR designer to increase the first stage stopband
        attenuation.
      + Cleaned up some of the code in the FIR designer.
      + Updated docs to reflect the above.
      + Update DAC settings to work for mic array base board as well.
      + Filter design script update for usability.
      + Documentation improvement.
      + Changed DEBUG_UNIT to XASSERT_UNIT to work with lib_xassert.
      + Added upgrade advisory.
      + Added dynamic range subsection to documentation.
      + Added ability to route internal channels of the output rate of the
        mic_array to the mic_array so that they can benefit from the post
        processing of the mic_array.
      + Enabled the metadata which delivers the frame counter.
      + Small fix to the filter generator to allow the use of fewer taps in the
        final stage FIR.
      + Added significant bits collection to the metadata.
      + Added fixed gain control through define MIC_ARRAY_FIXED_GAIN.
      + Tested and enabled the debug mode for detecting frame dropping. Enabled
        by adding DEBUG_MIC_ARRAY to the Makefile.
      + Moved to using types from lib_dsp.
      + Bug fix in python FIR generator script resulting in excessive output
        ripple.
      + Default FIR coefficients now optimised for 16kHz output sample rate.
      + Added ability to remap port pins to channels.
      + MIC_ARRAY_NUM_MICS is now forced to a multiple of 4 with a warning if it
        changed.
      + Corrected MIC_ARRAY_DC_OFFSET_LOG2 default value reporting in
        documentation.

    - lib_spdif: Added dependency 4.1.0

      + CHANGED:   Use XMOS Public Licence Version 1
      + CHANGED:   Rearrange documentation files

    - lib_voice: Removed dependency

    - lib_xassert: 2.0.1 -> 4.1.0

      + CHANGED: Use XMOS Public Licence Version 1
      + REMOVED: not necessary cpanfile
      + CHANGED: Pin Python package versions
      + CHANGED: Build files updated to support new "xcommon" behaviour in xwaf.
      + CHANGE: Correct dates in LICENSE.txt files
      + CHANGE: Renamed DEBUG_UNIT to XASSERT_UNIT to prevent conflict with
        lib_logging

    - lib_xua: Added dependency 3.2.0

      + CHANGED:   Updated tests to use lib_locks (was legacy module_locks)
      + CHANGED:   Exclude HID Report functions unless the HID feature is
        enabled
      + CHANGED:   Explicit feedback EP enabled by default (see
        UAC_FORCE_FEEDBACK_EP)
      + FIXED:     Incorrect conditional compilation of HID report code
      + FIXED:     Input/output descriptors written when input/output not
        enabled. (Audio class 1.0 mode using
        XUA_USB_DESCRIPTOR_OVERWRITE_RATE_RES)

    - lib_xud: Added dependency 2.1.0

      + CHANGE:    Various optimisations to aid corner-case timings on XS3 based
        devices
      + CHANGE:    Some API functions re-authored in C (were Assembly)
      + CHANGE:    Testbench now more accurately models XS3 based devices
      + CHANGE:    Endpoint functions called on a halted endpoint will block
        until the halt condition is cleared

    - sc_adat: Removed dependency

    - sc_i2c: Removed dependency

    - sc_spdif: Removed dependency

    - sc_usb: Removed dependency

    - sc_usb_audio: Removed dependency

    - sc_usb_device: Removed dependency

    - sc_util: Removed dependency

    - sc_xud: Removed dependency

6.18.1
------

  * CHANGE:    Updated PIDs in app_usb_aud_mic_array

  * Changes to dependencies:

    - lib_device_control: Added dependency 2.0.0

      + Added the ability to select USB interface (Allows control from Windows)

    - sc_usb_audio: 6.18.0 -> 6.18.1

      + ADDED:      Vendor Specific control interface added to UAC1 descriptors
        to allow control of XVSM params from Windows (via lib_usb)

6.18.0
------

  * ADDED:     app_usb_aud_mic_array now includes control of XVSM parameters
    (see lib_xvsm_support/host for host control applications)
  * RESOLVED:  Incorrect build configurations in Eclipse project files in
    app_usb_aud_mic_array

  * Changes to dependencies:

    - lib_voice: 0.0.2 -> 0.0.3

      + Added DOA_NAIVE_DONT_THRESH to disable thresholding code

    - sc_usb_audio: 6.16.0 -> 6.18.0

      + ADDED:      Call to VendorRequests() and VendorRequests_Init() to
        Endpoint 0
      + ADDED:      VENDOR_REQUESTS_PARAMS define to allow for custom parameters
        to VendorRequest calls
      + RESOLVED:   FIR gain compensation set appropriately in lib_mic_array
        usage
      + CHANGE:     i_dsp interface renamed i_audManage

    - sc_xud: 2.4.1 -> 2.4.2

      + CHANGE:     VBUS connection to xCORE-200 no longer required when using
        XUD_PWR_BUS i.e. for bus-powered devices. This removes the need to any
        protection circuitry and allows for a reduced BOM. Note, VBUS should
        still be present for self powered devices in order to pass USB
        compliance tests.
      + RESOLVED:   Device might hang during resume if host follows resume
        signality with activity after a time close to specified minimum of
        1.33us (#11813)

6.17.0
------

  * CHANGE:    app_usb_aud_mic array: Modifications to XVSM processing
    integration
  * CHANGE:    app_usb_aud_mic_array: AEC and NS enabled by default
  * CHANGE:    app_usb_aud_mic_array: XVSM VAD output used when DOA enabled

  * Changes to dependencies:

    - lib_voice: 0.0.1 -> 0.0.2

      + Simplification/optimisation of Naive DOA

6.16.1
------

  * CHANGE:    Feedback endpoint forcefully enabled in UAC1 build configs of
    app_usb_aud_mic array (workaround for Windows issue)
  * CHANGE:    XVSM processing has AEC enabled by default.
  * CHANGE:    Default gain increased for processed microphone data

6.16.0
------

  * ADDED:   XVSM enabled build config added to app_usb_mic_array. Includes
    example usage of UserBufferManagement() and i_dsp interface
  * CHANGE:  PDM Microphone processing examples use new interface (previously
    functional call)

  * Changes to dependencies:

    - lib_mic_array: 2.0.0 -> 2.0.1

      + Updated AN00221 to use new lib_dsp API for FFTs
      + Updates required for latest lib_mic_array_board_support API

    - lib_voice: Added dependency 0.0.1

      + Initial version

    - sc_usb_audio: 6.15.2 -> 6.16.0

      + ADDED:      Call to UserBufferManagement()
      + ADDED:      PDM_MIC_INDEX in devicedefines.h and usage
      + CHANGE:     pdm_buffer() task now combinable
      + CHANGE:     Audio I/O task now takes i_dsp interface as a parameter
      + CHANGE:     Removed built-in support for A/U series internal ADC
      + CHANGE:     User PDM Microphone processing now uses an interface
        (previously function call)

    - sc_usb_device: 1.3.8 -> 1.3.9

      + RESOLVED:   Value from HS config descriptor used for FS GET_STATUS
        request. Causes USB CV test fail.

6.15.2
------

  * CHANGE:    Design Guide updated for xCORE-200 MC Audio and xCORE Microphone
    array boards

  * Changes to dependencies:

    - sc_usb_audio: 6.15.1 -> 6.15.2

      + RESOLVED:   interrupt.h (used in audio buffering) now compatible with
        xCORE-200 ABI

6.15.1
------

  * ADDED:      Added build config to use TDM slave (2i8o8xxxxx_tdm8_slave) to
    app_usb_aud_xk_216_mc

  * Changes to dependencies:

    - lib_mic_array: 1.0.1 -> 2.0.0

      + Renamed all functions to match library structure
      + Decimator interface functions now take the array of
        mic_array_decimator_config structure rather than
        mic_array_decimator_config_common
      + All defines renames to match library naming policy
      + DC offset simplified
      + Added optional MIC_ARRAY_NUM_MICS define to save memory when using less
        than 16 microphones

    - sc_usb_audio: 6.15.0 -> 6.15.1

      + RESOLVED:   DAC data mis-alignment issue in TDM/I2S slave mode
      + CHANGE:     Updates to support API changes in lib_mic_array version 2.0

    - sc_xud: 2.4.0 -> 2.4.1

      + RESOLVED:   Initialisation failure on U-series devices

6.15.0
------

  * ADDED:      app_usb_aud_mic_array for xCORE Microphone Array board. Includes
    example usage of PDM microphone integration.

  * Changes to dependencies:

    - lib_logging: Added dependency 2.0.1

      + CHANGE:   Update to source code license and copyright

    - lib_mic_array: Added dependency 1.0.1

      + Added dynamic DC offset removal at startup to eliminate slow convergance
      + Mute first 32 samples to allow DC offset to adapt before outputting
        signal
      + Fixed XTA scripte to ensure timing is being met
      + Now use a 64-bit accumulator for DC offset removal
      + Consolidated generators into a single python generator
      + Produced output frequency response graphs
      + Added 16 bit output mode

    - lib_xassert: Added dependency 2.0.1

      + CHANGE: Update to source code license and copyright

    - sc_usb_audio: 6.14.0 -> 6.15.0

      + RESOLVED:   UAC 1.0 descriptors now support multi-channel volume control
        (previously were hard-coded as stereo)
      + CHANGE:     Removed 32kHz sample-rate support when PDM microphones
        enabled (lib_mic_array currently does not support non-integer decimation
        factors)

    - sc_util: 1.0.5 -> 1.0.6

      + xCORE-200 compatibility fixes to module_trycatch

6.14.0
------

  * ADDED:      UAC 1.0 build configs to app_usb_aud_xk_216_mc

  * Changes to dependencies:

    - sc_usb_audio: 6.13.0beta2 -> 6.14.0beta2

      + ADDED:      Support for for master-clock/sample-rate divides that are
        not a power of 2 (i.e. 32kHz from 24.567MHz)
      + ADDED:      Extended available sample-rate/master-clock ratios. Previous
        restriction was <= 512x (i.e. could not support 1024x and above e.g.
        49.152MHz MCLK for Sample Rates below 96kHz) (#13893)
      + ADDED:      Support for various "low" sample rates (i.e. < 44100) into
        UAC 2.0 sample rate list and UAC 1.0 descriptors
      + ADDED:      Support for the use and integration of PDM microphones
        (including PDM to PCM conversion) via lib_mic_array
      + RESOLVED:   MIDI data not accepted after "sleep" in OSX 10.11 (El
        Capitan) - related to sc_xud issue #17092
      + CHANGE:     Asynchronous feedback system re-implemented to allow for the
        first two ADDED changelog items
      + CHANGE:     Hardware divider used to generate bit-clock from master
        clock (xCORE-200 only). Allows easy support for greater number of
        master-clock to sample-rate ratios.
      + CHANGE:     module_queue no longer uses any assert module/lib

6.13.0
------

  * RESOLVED:   Channel string error & ADAT tx channel offset issue in
    app_usb_aud_l2 due to SPDIF define typo in customdefines.h (should have been
    SPDIF_TX)
  * RESOLVED:   Incorrect I2C addresses of CODECs in app_usb_aud_skc_u16

  * Changes to dependencies:

    - sc_usb_audio: 6.12.5rc0 -> 6.13.0beta2

      + ADDED:      Device now uses implicit feedback when input stream is
        available (previously explicit feedback pipe always used). This saves
        chanend/EP resources and means less processing burden for the host.
        Previous behaviour available by enabling UAC_FORCE_FEEDBACK_EP
      + RESOLVED:   Exception when SPDIF_TX and ADAT_TX both enabled due to
        clock-block being configured after already started. Caused by SPDIF_TX
        define check typo
      + RESOLVED:   DFU flag address changed to properly conform to memory
        address range allocated to apps by tools
      + RESOLVED:   Build failure when DFU disabled
      + RESOLVED:   Build issue when I2S_CHANS_ADC/DAC set to 0 and CODEC_MASTER
        enabled
      + RESOLVED:   Typo in MCLK_441 checking for MIN_FREQ define
      + CHANGE:     Mixer and non-mixer channel comms scheme (decouple <-> audio
        path) now identical
      + CHANGE:     Input stream buffering modified such that during overflow
        older samples are removed rather than ignoring most recent samples.
        Removes any chance of stale input packets being sent to host
      + CHANGE:     module_queue (in sc_usb_audio) now uses lib_xassert rather
        than module_xassert
      + RESOLVED:   Build error when DFU is disabled
      + RESOLVED:   Build error when I2S_CHANS_ADC or I2S_CHANS_DAC set to 0 and
        CODEC_MASTER enabled

    - sc_usb_device: 1.3.7rc0 -> 1.3.8beta0

    - sc_xud: 2.3.2rc0 -> 2.4.0beta0

      + RESOLVED:   Intermittent initialisation issues with xCORE-200
      + RESOLVED:   SETUP transaction data CRC not properly checked
      + RESOLVED:   RxError line from phy handled
      + RESOLVED:   Isochronous IN endpoints now send an 0-length packet if not
        ready rather than an (invalid) NAK.
      + RESOLVED:   Receive of short packets sometimes prematurely ended
      + RESOLVED:   Data PID not reset to DATA0 in ClearStallByAddr() (used on
        ClearFeature(HALT) request from host) (#17092)

6.12.6
------

  * Changes to dependencies:

    - sc_usb_audio: 6.12.2rc3 -> 6.12.5rc0

      + RESOLVED:   Stream issue when NUM_USB_CHAN_IN < I2S_CHANS_ADC
      + RESOLVED:   DFU fail when DSD enabled and USB library not running on
        tile[0]
      + RESOLVED:   Method for storing persistent state over a DFU reboot
        modified to improve resilience against code-base and tools changes

6.12.5
------

  * RESOLVED:   Enabled DFU support (and quad-SPI flash) support in xCORE-200
    application.
  * RESOLVED:   Link names updated in xCORE-200 XN file
  * CHANGE:     xCore-200 Role-change reboot code updated for tools versions >
    14.0.2

  * Changes to dependencies:

    - sc_usb_audio: 6.12.1alpha0 -> 6.12.3rc0

      + RESOLVED:   Method for storing persistent state over a DFU reboot
        modified to improve resilience against code-base and tools changes
      + RESOLVED:   Reboot code (used for DFU) failure in tools versions >
        14.0.2 (xCORE-200 only)
      + RESOLVED:   Run-time exception in mixer when MAX_MIX_COUNT > 0
        (xCORE-200 only)
      + RESOLVED:   MAX_MIX_COUNT checked properly for mix strings in string
        table
      + CHANGE:     DFU code re-written to use an XC interface. The flash-part
        may now be connected to a separate tile to the tile running USB code
      + CHANGE:     DFU code can now use quad-SPI flash
      + CHANGE:     Example xmos_dfu application now uses a list of PIDs to
        allow adding PIDs easier. --listdevices command also added.
      + CHANGE:     I2S_CHANS_PER_FRAME and I2S_WIRES_xxx defines tidied

6.12.4
------

  * RESOLVED:   (Minor) Fixed build issue with iAP EA Native Transport endpoints
    example code in app_usb_aud_skc_u16_audio8
  * ADDED:      Support for xCORE-200 MC AUDIO board version 2.0 (in
    app_usb_aud_x200)
  * ADDED:      ADAT output/input build configuration to app_usb_aud_x200
  * ADDED:      SPDIF input build configuration to app_usb_aud_x200
  * CHANGE:     Rationalised build config naming in app_usb_aud_x200

  * Changes to dependencies:

    - sc_spdif: 1.3.3alpha2 -> 1.3.4alpha0

      + Changes to RX codebase to allow running on xCORE-200

    - sc_usb_audio: 6.12.0alpha1 -> 6.12.1alpha0

      + RESOLVED:   Fixes to TDM input timing/sample-alignment when BCLK=MCLK
      + RESOLVED:   Various minor fixes to allow ADAT_RX to run on xCORE 200 MC
        AUDIO hardware
      + CHANGE:     Moved from old SPDIF define to SPDIF_TX

6.12.3
------

  * ADDED:      Added roleswitch compatible build config to app_usb_aud_x200
  * CHANGE:     iPod detect code upataed and USB mux set appropriately for
    roleswitch (guarded by USB_SEL_A)
  * CHANGE:     Updated all interrupts used for role-switch to new interrupt.h
    API

  * Changes to dependencies:

    - sc_usb_device: 1.3.6alpha0 -> 1.3.7alpha0

    - sc_xud: 2.3.1alpha0 -> 2.3.2alpha0

      + CHANGE:     Interrupts disabled during any access to usb_tile. Allows
        greater reliability if user suspend/resume functions enabled interrupts
        e.g. for role-switch

6.12.2
------

  * ADDED:      Example code for using iAP EA Native Transport endpoints to
    app_usb_aud_x200

6.12.1
------

  * ADDED:      DSD enabled build configurations to app_usb_aud_x200
  * CHANGE:     GPIO access in app_usb_aud_x200 guarded with a lock for safety

6.12.0
------

  * ADDED:      app_usb_aud_x200 application for xCORE-200-MC-AUDIO board
  * CHANGE:     Varous I2C device addresses updated for new I2C API.
  * CHANGE:     Added I2C module as an explicy dependancy to various apps where
    module_i2c_shared is used (previously module_i2c_shared had
    module_i2c_simple as a dependancy)
  * CHANGE:     I2C ports now in structs as required to match new I2C module API

  * Changes to dependencies:

    - sc_i2c: 2.4.1rc1 -> 3.0.0alpha1

      + Read support added to module_i2c_single_port (xCORE 200 only)
      + Retry on NACK added to module_i2c_single_port (matches
        module_i2c_simple)
      + module_i2c_single_port functions now takes struct for port resources
        (matches module_i2c_simple)
      + module_i2c_simple removed from module_i2c_shared dependancies. Allows
        use with other i2c modules. It is now the applications responsibilty to
        include the desired i2c module as a depenancy.
      + Data arrays passed to write_reg functions now marked const

    - sc_spdif: 1.3.2rc2 -> 1.3.3alpha2

    - sc_usb_audio: 6.11.2rc2 -> 6.12.0alpha1

      + ADDED:      Checks for XUD_200_SERIES define where required
      + RESOLVED:   Run-time exception due to decouple interrupt not entering
        correct issue mode (affects XCORE-200 only)
      + CHANGE:     SPDIF Tx Core may now reside on a different tile from I2S
      + CHANGE:     I2C ports now in structure to match new
        module_i2c_singleport/shared API.
      + RESOLVED:  (Major) Streaming issue when mixer not enabled (introduced in
        6.11.2)

    - sc_usb_device: 1.3.5rc2 -> 1.3.6alpha0

    - sc_util: 1.0.4rc0 -> 1.0.5alpha0

      + xCORE-200 compatibility fixes to module_locks

    - sc_xud: 2.2.4rc3 -> 2.3.0alpha0

      + ADDED:      Support for XCORE-200 (libxud_x200.a)
      + CHANGE:     Compatibility fixes for XMOS toolset version 14 (dual-issue
        support etc)

6.11.2
------

  * ADDED:      S/PDIF & ADAT input enabled build configs to
    app_usb_aud_skc_u16_audio8 including required external Cirrus fractional-N
    configuration.
  * CHANGE:     Example HID code uses defines from module_usb_audio/user_hid.h
  * CHANGE:     module_usb_audio_adat replaced with module_adat from sc_adat

  * Changes to dependencies:

    - sc_usb_audio: 6.11.1beta2 -> 6.11.2rc2

      + RESOLVED:   (Major) Enumeration issue when MAX_MIX_COUNT > 0 only.
        Introduced in mixer optimisations in 6.11.0. Only affects designs using
        mixer functionality.
      + RESOLVED:   (Normal) Audio buffering request system modified such that
        the mixer output is not silent when in underflow case (i.e. host output
        stream not active) This issue was introduced with the addition of DSD
        functionality and only affects designs using mixer functionality.
      + RESOLVED:   (Minor) Potential build issue due to duplicate labels in
        inline asm in set_interrupt_handler macro
      + RESOLVED:   (Minor) BCD_DEVICE define in devicedefines.h now guarded by
        ifndef (caused issues with DFU test build configs.
      + RESOLVED:   (Minor) String descriptor for Clock Selector unit
        incorrectly reported
      + RESOLVED:   (Minor) BCD_DEVICE in devicedefines.h now guarded by #ifndef
        (Caused issues with default DFU test build configs.
      + CHANGE:     HID report descriptor defines added to shared user_hid.h
      + CHANGE:     Now uses module_adat_rx from sc_adat (local
        module_usb_audio_adat removed)

6.11.1
------

  * ADDED:      ADAT transmit enabled build configs to app_usb_aud_l2
  * ADDED:      Audio hardware configuration for XCore I2S slave mode to
    app_usb_aud_skc_u16_audio8 when CODEC_MASTER enabled.
  * ADDED:      Build configurations in app_usb_aud_l2 for TDM
  * ADDED:      DAC/ADC configuration for TDM in app_usb_aud_l2 when
    I2S_MODE_TDM enabled.

  * Changes to dependencies:

    - sc_usb_audio: 6.11.0alpha2 -> 6.11.1beta2

      + ADDED:      ADAT transmit functionality, including SMUX. See ADAT_TX and
        ADAT_TX_INDEX.
      + RESOLVED:   (Normal) Build issue with CODEC_MASTER (xCore is I2S slave)
        enabled
      + RESOLVED:   (Minor) Channel ordering issue in when TDM and CODEC_MASTER
        mode enabled
      + RESOLVED:   (Normal) DFU fails when SPDIF_RX enabled due to clock block
        being shared between SPDIF core and FlashLib

6.11.0
------

  * ADDED:      Build configurations in app_usb_aud_skc_u16_audio8 for TDM
  * ADDED:      DAC/ADC configuration for TDM in app_usb_aud_skc_u16_audio8 when
    I2S_MODE_TDM enabled.

  * Changes to dependencies:

    - sc_usb_audio: 6.10.0alpha2 -> 6.11.0alpha2

      + ADDED:      Basic TDM I2S functionality added. See I2S_CHANS_PER_FRAME
        and I2S_MODE_TDM
      + CHANGE:     Various optimisations in 'mixer' core to improve performance
        for higher channel counts including the use of XC unsafe pointers
        instead of inline ASM
      + CHANGE:     Mixer mapping disabled when MAX_MIX_COUNT is 0 since this is
        wasted processing.
      + CHANGE:     Descriptor changes to allow for channel input/output channel
        count up to 32 (previous limit was 18)

6.10.0
------

  * CHANGE:     Support for version 2V0 of XK-USB-AUDIO-U8-2C and XP-SKC-U16
    core boards and XA-SK-USB-BLC and XA-SK-USB-ABC slices in
    app_usb_aud_xk_u8_2c and app_usb_aud_skc_u16_audio8 (previous board versions
    will not operate correctly without software modification)
  * RESOLVED:   (minor) AudioHwConfig() in app_usb_aud_l2 now writes correct
    register value to CS42448 CODEC for MCLK frequencies in the range 25MHz to
    51MHz.

  * Changes to dependencies:

    - sc_usb_audio: 6.9.0alpha0 -> 6.10.0alpha2

      + CHANGE:     Endpoint management for iAP EA Native Transport now merged
        into buffer() core. Previously was separate core (as added in 6.8.0).
      + CHANGE:     Minor optimisation to I2S port code for inputs from ADC

    - sc_usb_device: 1.3.4rc0 -> 1.3.5rc2

      + RESOLVED:   (Minor) Design Guide documentation build errors

    - sc_xud: 2.2.3rc0 -> 2.2.4rc3

      + RESOLVED:   (Minor) Potential for lock-up when waiting for USB clock on
        startup. This is is avoided by enabling port buffering on the USB clock
        port. Affects L/G series only.

6.9.0
-----

  * ADDED:    Added ADAT Rx enabled build config in app_usb_aud_l2

  * Changes to dependencies:

    - sc_usb_audio: 6.8.0alpha2 -> 6.9.0alpha0

      + ADDED:      ADAT S-MUX II functionality (i.e. 2 channels at 192kHz) -
        Previously only S-MUX supported (4 channels at 96kHz).
      + ADDED:      Explicit build warnings if sample rate/depth & channel
        combination exceeds available USB bus bandwidth.
      + RESOLVED:   (Major) Reinstated ADAT input functionality, including
        descriptors and clock generation/control and stream configuration
        defines/tables.
      + RESOLVED:   (Major) S/PDIF/ADAT sample transfer code in audio() (from
        ClockGen()) moved to aid timing.
      + CHANGE:     Modifying mix map now only affects specified mix, previous
        was applied to all mixes. CS_XU_MIXSEL control selector now takes values
        0 to MAX_MIX_COUNT + 1 (with 0 affecting all mixes).
      + CHANGE:     Channel c_dig_rx is no longer nullable, assists with timing
        due to removal of null checks inserted by compiler.
      + CHANGE:     ADAT SMUX selection now based on device sample frequency
        rather than selected stream format - Endpoint 0 now configures
        clockgen() on a sample-rate change rather than stream start.

    - sc_usb_device: 1.3.3alpha0 -> 1.3.4rc0

    - sc_xud: 2.2.2alpha0 -> 2.2.3rc0

      + RESOLVED:   (Minor) XUD_ResetEpStateByAddr() could operate on
        corresponding OUT endpoint instead of the desired IN endpoint address as
        passed into the function (and vice versa)

6.8.0
-----

  * ADDED:    Mixer enabled config to app_usb_aud_l2 Makefile
  * ADDED:    Example code for using iAP EA Native Transport endpoints to
    app_usb_aud_skc_u16_audio8
  * ADDED:    Example LED level metering code to app_usb_aud_l2

  * Changes to dependencies:

    - sc_usb: 1.0.3rc0 -> 1.0.4alpha0

      + ADDED:      Structs for Audio Class 2.0 Mixer and Extension Units

    - sc_usb_audio: 6.7.0alpha0 -> 6.8.0alpha2

      + ADDED:      Evaluation support for iAP EA Native Transport endpoints
      + RESOLVED:   (Minor) Reverted change in 6.5.1 release where sample rate
        listing in Audio Class 1.0 descriptors was trimmed (previously 4 rates
        were always reported). This change appears to highlight a Windows (only)
        enumeration issue with the Input & Output configs
      + RESOLVED:   (Major) Mixer functionality re-instated, including
        descriptors and various required updates compatibility with 13 tools
      + RESOLVED:   (Major) Endpoint 0 was requesting an out of bounds channel
        whilst requesting level data
      + RESOLVED:   (Major) Fast mix code not operates correctly in 13 tools,
        assembler inserting long jmp instructions
      + RESOLVED:   (Minor) LED level meter code now compatible with 13 tools
        (shared mem access)
      + RESOLVED    (Minor) Ordering of level data from the device now matches
        channel ordering into mixer (previously the device input data and the
        stream from host were swapped)
      + CHANGE:     Level meter buffer naming now resemble functionality

    - sc_usb_device: 1.3.2rc0 -> 1.3.3alpha0

    - sc_xud: 2.2.1rc0 -> 2.2.2alpha0

      + CHANGE:     Header file comment clarification only

6.7.0
-----

  * CHANGE:     Audio interrupt endpoint implementation simplified (use for
    notifying host of clock validity changes) simplified. Decouple() no longer
    involved.
  * RESOLVED:   Makefile issue for 2ioxx config in app_usb_aud_skc_su1
  * RESOLVED:   Support for S/PDIF input reinstated (includes descriptors,
    clocking support etc)

  * Changes to dependencies:

    - sc_usb_audio: 6.6.1rc1 -> 6.7.0alpha0

6.6.1
-----

  * ADDED:      Documentation for DFU
  * ADDED:      XUD_PWR_CFG define
  * CHANGE:     DSD ports now only enabled once to avoid potential lock up on
    DSD->PCM mode change due to un-driven line floating high.
    ConfigAudioPortsWrapper() also simplified.

  * Changes to dependencies:

    - sc_usb_audio: 6.6.0rc2 -> 6.6.1rc1

    - sc_usb_device: 1.3.0rc0 -> 1.3.2rc0

    - sc_xud: 2.1.1rc0 -> 2.2.1rc0

      + RESOLVED:   Slight optimisations (long jumps replaced with short) to aid
        inter-packet gaps.
      + CHANGE:     Timer usage optimisation - usage reduced by one.
      + CHANGE:     OTG Flags register explicitly cleared at start up - useful
        if previously running in host mode after a soft-reboot.

6.6.0
-----

  * ADDED:      Added app_usb_aud_skc_u16_audio8 application for XP-SKC-U16 with
    XA-SK-AUDIO8
  * CHANGE:     Support for XA-SK-USB-BLC 1V2 USB slice in app_usb_aud_xk_u8_2c
    and app_usb_aud_skc_u16 (1V1 slices will not operate correctly without
    software modification)
  * CHANGE:     Removed app_usb_aud_su1
  * CHANGE:     Endpoint 0 code updated to support new XUD test-mode enable API
  * CHANGE:     Macs operation for volume processing in mixer core now retains
    lower bits when device configured to use either 32bit samples or Native DSD.
  * RESOLVED:   (Minor) DFU_FLASH_DEVICE define corrected in
    app_usb_aud_skc_u16. Previously an incorrect SPI spec was defined causing
    DFU to fail for this example application.
  * RESOLVED:   (Minor) HID descriptor properly defined when HID_CONTROLS
    enabled

  * Changes to dependencies:

    - sc_usb_audio: 6.5.1rc4 -> 6.6.0rc2

    - sc_usb_device: 1.2.2rc4 -> 1.3.0rc0

      + CHANGE:  Required updates for XUD API change relating to USB
        test-mode-support

    - sc_xud: 2.0.1rc3 -> 2.1.1rc0

      + ADDED:      Warning emitted when number of cores is greater than 6
      + CHANGE:     XUD no longer takes a additional chanend parameter for
        enabling USB test-modes. Test-modes are now enabled via a
        XUD_SetTestMode() function using a chanend relating to Endpoint 0. This
        change was made to reduce chanend usage only.

6.5.1
-----

  * ADDED:      Added USB Design Guide to this repo including major update (see
    /doc)
  * ADDED:      Added MIDI_RX_PORT_WIDTH define such that a 4-bit port can be
    used for MIDI Rx
  * CHANGE:     I2S data to clock edge setup time improvements when BCLK = MCLK
    (particularly when running at 384kHz with a 24.576MHz master-clock)
  * CHANGE:     String table rationalisation (now based on a structure rather
    than a global array)
  * CHANGE:     Channel strings now set at build-time (rather than run-time)
    avoiding the use of memcpy
  * CHANGE:     Re-added c_aud_cfg channel (guarded by AUDIO_CFG_CHAN) allowing
    easy communication of audio hardware config to a remote core
  * CHANGE:     Channel strings now labeled "Analogue X, SPDIF Y" if S/PDIF and
    Analogue channels overlap (previously Analogue naming took precedence)
  * CHANGE:     Stream sample resolution now passed though to audio I/O core -
    previously only the buffering code was notified. AudioHwConfig() now takes
    parameters for sample resolution for DAC and ADC
  * CHANGE:     Endpoint0 core only sends out notifications of stream format
    change on stream start event if there is an actual change in format (e.g.
    16bit to 24bit or PCM to DSD). This avoids unnecessary audio I/O restarts
    and reconfiguration of external audio hardware (via AudioHwConfig())
  * CHANGE:     All occurances of historical INPUT and OUTPUT defines now
    removed. NUM_USB_CHAN_IN and NUM_USB_CHAN_OUT now used throughout the
    codebase.
  * RESOLVED:   (Minor) USB test mode requests re-enabled - previously was
    guarded by TEST_MODE_SUPPORT in module_usb_device (#15385)
  * RESOLVED:   (Minor) Audio Class 1.0 sample frequency list now respects
    MAX_FREQ (previously based on OUTPUT and INPUT defines) (#15417)
  * RESOLVED:   (Minor) Audio Class 1.0 mute control SET requests stalled due to
    incorrect data length check (#15419)
  * RESOLVED    (Minor) DFU Upload request now functional (Returns current
    upgrade image to host) (#151571)

  * Changes to dependencies:

    - sc_i2c: 2.4.0beta1 -> 2.4.1rc1

      + module_i2c_simple header-file comments updated to correctly reflect API

    - sc_spdif: 1.3.1beta3 -> 1.3.2rc2

    - sc_usb_audio: 6.5.0beta2 -> 6.5.1rc4

    - sc_usb_device: 1.1.0beta0 -> 1.2.2rc4

      + RESOLVED:   (Minor) Build issue in Windows host app for bulk demo
      + CHANGE:     USB_StandardRequests() now returns XUD_Result_t instead of
        int
      + CHANGE:     app_hid_mouse_demo now uses XUD_Result_t
      + CHANGE:     app_custom_bulk_demo now uses XUD_Result_t
      + CHANGE:     USB_StandardRequests() now takes the string table as an
        array of char pointers rather than a fixed size 2D array. This allows
        for a more space efficient string table representation. Please note,
        requires tools 13 or later for XC pointer support.
      + CHANGE:     Demo applications now set LangID string at build-time
        (rather than run-time)
      + CHANGE:     Test mode support no longer guarded by TEST_MODE_SUPPORT

    - sc_util: 1.0.3rc0 -> 1.0.4rc0

      + module_logging now compiled at -Os
      + debug_printf in module_logging uses a buffer to deliver messages
        unfragmented
      + Fix thread local storage calculation bug in libtrycatch
      + Fix debug_printf itoa to work for unsigned values > 0x80000000

    - sc_xud: 2.0.0beta1 -> 2.0.1rc3

      + RESOLVED:   (Minor) Error when building module_xud in xTimeComposer due
        to invalid project files.

6.5.0
-----

  * CHANGE:     USB Test mode support enabled by default (required for
    compliance testing)
  * CHANGE:     Default full-speed behaviour is now Audio Class 2, previously
    was a null device
  * CHANGE:     Various changes to use XUD_Result_t returned from XUD functions
  * CHANGE:     All remaining references to ARCH_x defines removed.
    XUD_SERIES_SUPPORT should now be used (#15270)
  * CHANGE:     Added IAP_TILE and MIDI_TILE defines (default to AUDIO_IO_TILE)
    (#15271)
  * CHANGE:     Multiple output stream formats now supported. See
    OUTPUT_FORMAT_COUNT and various _STREAM_FORMAT_OUTPUT_ defines. This allows
    dynamically selectable streaming interfaces with different formats e.g.
    sub-slot size, resolution etc. 16bit and 24bit enabled by default
  * CHANGE:     Audio buffering code now handles different slot size for
    input/output streams
  * CHANGE:     Endpoint 0 code now in standard C (rather than XC) to allow
    better use of packed structures for descriptors
  * CHANGE:     Use of structures/enums/headers in module_usb_shared to give
    more modular Audio Class 2.0 descriptors that can be more easily modified at
    run-time
  * CHANGE:     16bit audio buffer packing/unpacking optimised
  * RESOLVED:   (Minor) All access to port32A now guarded by locks in
    app_usb_aud_xk_u8_2c
  * RESOLVED:   (Minor) iAP interface string index in descriptors when MIXER
    enabled (#15257)
  * RESOLVED:   (Minor) First feedback packet could be the wrong size (3 vs 4
    byte) after a bus- speed change. usb_buffer() core now explicitly re-sizes
    initial feedback packet on stream-start based on bus-speed
  * RESOLVED:   (Minor) Preprocessor error when AUDIO_CLASS_FALLBACK enabled and
    FULL_SPEED_AUDIO_2 not defined. FULL_SPEED_AUDIO_2 now only enabled by
    default if AUDIO_CLASS_FALLBACK is not enabled (#15272)
  * RESOLVED:   (Minor) XUD_STATUS_ENABLED set for iAP IN endpoints (and
    disabled for OUT endpoint) to avoid potential stale buffer being transmitted
    after bus-reset.

6.4.1
-----

  * RESOLVED:   (Minor) MIDI on single-tile L series devices now functional.
    CLKBLK_REF no longer used for MIDI when running on the same tile as
    XUD_Manager()

6.4.0
-----

  * ADDED:      XK-USB-AUDIO-U8-2C mute output driven high when audiostream not
    active (app_usb_aud_xk_u8_2c)
  * CHANGE:     MIDI ports no longer passed to MFi specific functions
  * CHANGE:     Audio delivery core no longer waits for AUDIO_PLL_LOCK_DELAY
    after calling AudioHwConfig() and running audio interfaces. It should be
    ensured that AudioHwConfig() implementation should handle any delays
    required for stable MCLK as required by the clocking hardware.
  * CHANGE:     Delay to allow USB feedback to stabilise after sample-rate
    change now based on USB bus speed. This allows faster rate change at
    high-speed.
  * CHANGE:     FL_DEVICE flash spec macros (from flash.h) used for
    DFU_FLASH_DEVICE define where appropriate rather than defining the spec
    manually
  * RESOLVED:   (Major) Broken (noisy) playback in DSD native mode (introduced
    in 6.3.2). Caused by 24bit (over 32bit) volume processing when DSD enabled -
    DSD bits are lost. 24bit volume control now guarded by NATIVE_DSD define
    (#15200)
  * RESOLVED:   (Minor) Default for SPDIF define set to 1 in app_usb_aud_l1
    customdefines.h. Previously SPDIF not properly enabled in binaries (#15129)
  * RESOLVED:   (Minor) All remaining references to stdcore[] replaced with
    tile[] (#15122)
  * RESOLVED:   (Minor) Removed hostactive.xc and audiostream.xc from
    app_usb_aud_skc_u16 such that default implementations are used
    (hostactive.xc was using an invalid port) (#15118)
  * RESOLVED:   (Minor) The next 44.1 based freq above MAX_FREQ was reported by
    GetRange(SamplingFrequency) when MAX_FREQ = MIN_FREQ (and MAX_FREQ was 48k
    based) (#15127)
  * RESOLVED:   (Minor) MIDI input events no longer intermittently dropped under
    heavy output traffic (Typically SysEx) from USB host - MIDI Rx port now
    buffered (#14224)
  * RESOLVED:   (Minor) Fixed port mapping in app_usb_aud_skc_u16 XN file
    (#15124)
  * RESOLVED:   (Minor) DEFAULT_FREQ was assumed to be a multiple of 48k during
    initial calculation of g_SampFreqMultiplier (#15141)
  * RESOLVED:   (Minor) SPDIF not properly enabled in any build of
    app_usb_aud_l1 (SPDIF define set to 0 in customdefines.h) (#15102)
  * RESOLVED:   (Minor) DFU enabled by default in app_usb_aud_l2 (#15153)
  * RESOLVED:   (Minor) Build issue when NUM_USB_CHAN_IN or NUM_USB_CHAN_OUT set
    to 0 and MIXER set to 1 (#15096)
  * RESOLVED:   (Minor) Build issue when CODEC_MASTER set (#15162)
  * RESOLVED:   (Minor) DSD mute pattern output when invalid DSD frequency
    selected in Native DSD mode. Previously 0 was driven resulting in pop noises
    on the analague output when switching between DSD/PCM (#14769)
  * RESOLVED:   (Minor) Build error when OUT_VOLUME_IN_MIXER was set to 0
    (#10692)
  * RESOLVED:   (Minor) LR channel swap issue in CS42448 CODEC by more closely
    matching recommended power up sequence (app_usb_aud_l2) (#15189)
  * RESOLVED:   (Minor) Improved the robustness of ADC I2S data port init when
    MASTER_CODEC defined (#15203)
  * RESOLVED:   (Minor) Channel counts in Audio 2 descriptors now modified based
    on bus-speed. Input stream format also modified (previously only output was)
    (#15202)
  * RESOLVED:   (Minor) Full-speed Audio Class 2.0 sample-rate list properly
    restricted based on if input /output are enabled (#15210)
  * RESOLVED:   (Minor) AUDIO_CLASS_FALLBACK no longer required to be defined
    when AUDIO_CLASS set to 1 (#13302)

  * Changes to dependencies:

    - sc_usb: 1.0.1beta1 -> 1.0.2beta1

      + ADDED:      USB_BMREQ_D2H_VENDOR_DEV and USB_BMREQ_D2H_VENDOR_DEV
        defines for vendor device requests

    - sc_usb_device: 1.0.3beta0 -> 1.0.4beta5

      + CHANGE:     devDesc_hs and cfgDesc_hs params to USB_StandardRequests()
        now nullable (useful for full-speed only devices)
      + CHANGE:     Nullable descriptor array parameters to
        USB_StandardRequests() changed from ?array[] to (?&array)[] due to the
        compiler warning that future compilers will interpret the former as an
        array of nullable items (rather than a nullable reference to an array).
        Note: The NULLABLE_ARRAY_OF macro (from xccompat.h) is used retain
        compatibility with older tools version (i.e. 12).

    - sc_xud: 1.0.2alpha1 -> 1.0.3beta1

      + RESOLVED:   (Minor) ULPI data-lines driven hard low and XMOS pull-up on
        STP line disabled before taking the USB phy out of reset. Previously the
        phy could clock in erroneous data before the XMOS ULPI interface was
        initialised causing potential connection issues on initial startup. This
        affects L/G series libraries only.
      + RESOLVED:   (Minor) Fixes to improve memory usage such as adding missing
        resource usage symbols/elimination blocks to assembly file and inlining
        support functions where appropriate.
      + RESOLVED:   (Minor) Moved to using supplied tools support for
        communicating with the USB tile rather than custom implementation
        (affects U-series lib only).

6.3.2
-----

  * ADDED:      SAMPLE_SUBSLOT_SIZE_HS/SAMPLE_SUBSLOT_SIZE_FS defines (default
    4/3 bytes)
  * ADDED:      SAMPLE_BIT_RESOLUTION_HS/SAMPLE_BIT_RESOLUTION_FS defines
    (default 24/24 bytes)
  * CHANGE:     PIDs in app_usb_aud_xk_2c updated (previously shared with
    app_usb_aud_skc_su1). Requires Thesycon 2.15 or later
  * RESOLVED:   (Minor) Fixed maxPacketSize for audio input endpoint (was
    hard-coded to 1024)

  * Changes to dependencies:

    - sc_usb_device: 1.0.2beta0 -> 1.0.3beta0

    - sc_xud: 1.0.1beta3 -> 1.0.2alpha1

      + ADDED:      Re-instated support for G devices (xud_g library)

6.3.1
-----

  * ADDED:      Reinstated application for XR-USB-AUDIO-2.0-MC board
    (app_usb_aud_l2)
  * ADDED:      Support for operation with Apple devices (MFI licensees only -
    please contact XMOS)
  * ADDED:      USER_MAIN_DECLARATIONS and USER_MAIN_CORES defines in main for
    easy addition of custom cores
  * CHANGE:     Access to shared GPIO port (typically 32A) in app code now
    guarded with a lock for safety
  * CHANGE:     Re-organised main() to call two functions with the aim to
    improve readability
  * CHANGE:     Event queue logic in MIDI now in XC module-queue such that it
    can be inlined (code-size saving)
  * CHANGE:     Various functions now marked static to encourage inlining,
    saving around 200 bytes of code-size
  * CHANGE:     Removed redundant MIDI buffering code from previous buffering
    scheme
  * CHANGE:     Some tidy of String descriptors table and related defines

  * Changes to dependencies:

    - sc_i2c: 2.2.1rc0 -> 2.3.0beta1

      + module_i2c_simple fixed to ACK correctly during multi-byte reads (all
        but the final byte will be now be ACKd)
      + module_i2c_simple can now be built with support to send repeated starts
        and retry reads and writes NACKd by slave
      + module_i2c_shared added to allow multiple logical cores to safely share
        a single I2C bus
      + Removed readreg() function from single_port module since it was not safe

    - sc_spdif: 1.3.0rc4 -> 1.3.1beta2

      + Added .type and .size directives to SpdifReceive. This is required for
        the function to show up in xTIMEcomposer binary viewer

6.3.0
-----

  * ADDED:      Application for XP-SKC-U16 board with XA-SK-AUDIO slice
    (app_usb_aud_xkc_u16)
  * CHANGE:     Moved to XMOS toolchain version 13

6.2.1
-----

  * ADDED:      DEFAULT_MCLK_FREQ define added
  * RESOLVED:   Native DSD now easily disabled whilst keeping DoP mode enabled
    (setting NATIVE_DSD to 0 with DSD_CHANS_DAC > 0)
  * RESOLVED:   Device could become unresponsive if the host outputs a stream
    with an invalid DoP frequency (#14938)

6.2.0
-----

  * ADDED:      Application for XK-USB-AUDIO-U8-2C board
  * ADDED:      PRODUCT_STR define for Product Strings
  * ADDED:      Added DSD over PCM (DoP) mode
  * ADDED:      Added Native DSD (Driver support required)
  * ADDED:      Added optional channel for audio buffing control, this can
    reduce power consumption
  * ADDED:      The device can run in Audio Class 2.0 when connected to a
    full-speed hub using the FULL_SPEED_AUDIO_2 define
  * ADDED:      MIN_FREQ configuration define for setting minimum sample rate of
    device (previously assumed 44.1)
  * CHANGE:     Endpoint0 code migrated to use new module_usb_device shared
    module
  * CHANGE:     Device reboot code (for DFU) made more generic for multi-tile
    systems
  * CHANGE:     DFU code now erases all upgrade images found, rather than just
    the first one
  * CHANGE:     ports.h file no longer required.  Please declare custom ports in
    your own files
  * CHANGE:     Define based warnings in devicedefines.h moved to warnings.xc to
    avoid multiple warnings being issued
  * RESOLVED:   (Major) ADC port initialization did not operate as expected at
    384kHz
  * RESOLVED:   (Major) Resolved a compatibility issue with streaming on Intel
    USB 3.0 xHCI host controller
  * RESOLVED:   (Major) Added defence against malformed Audio Class 1.0 packets
    as experienced on some Win 8.0 hosts. Previously this would cause an
    exception (Issue fixed in Win 8.1)
  * RESOLVED:   (Minor)  maxPacketSize now reported based on device's read
    bandwidth requirements. This allows the driver to reserve the proper
    bandwidth amount (previously bandwidth would have been wasted)
  * RESOLVED:   (Minor) Input channel strings used for output in one instance
  * RESOLVED:   (Minor) Volume multiplication now compatible with 32bit samples.
    Previously assumed 24bit samples and would truncate bottom 3 bits
  * RESOLVED:   (Minor) Fixed issue with SE0_NAK test mode (as required for
    device receiver sensitivity USB-IF compliance test
  * RESOLVED:   (Minor) Fixed issue with packet parameters compliance test
  * RESOLVED:   (Minor) Added bounds checking to string requests. Previously an
    exception was raised if an invalid String was requested

6.1.0
-----

  * RESOLVED:   Resolved issue with DFU caused by SU1 ADC usage causing issues
    with soft reboot
  * ADDED:      Added ability for channel count changes between UAC1 and UAC2
    modes
  * ADDED:      Support for iOS authentication (MFI licencees only - please
    contact XMOS)

6.0.1
-----

  * CHANGE:     Removed support for early engineering sample U-series devices

6.0.0
-----

  * ADDED:      Support for SU1 (Via SU1 Core Board and Audio Slice) - see
    app_usb_aud_skc_su1
  * ADDED:      Design moved to new build system
  * ADDED:      Optional support for USB test modes
  * ADDED:      Optional HID endpoint for audio controls and example usages
  * ADDED:      Multiple build configurations for supported device
    configurations
  * CHANGE:     Now uses latest XUD API
  * CHANGE:     MIDI buffering simplified (using new XUD API) - no longer goes
    through decouple thread
  * CHANGE:     Now uses sc_i2c from www.github.com/xcore/sc_i2c
  * CHANGE:     Previous default serial string of "0000" removed. No serial
    string now reported.
  * CHANGE:     Master volume update optimised slightly (updateMasterVol in
    audiorequests.xc)
  * CHANGE:     Master volume control disabled in Audio Class 1.0 mode to solve
    various issues in Windows
  * CHANGE:     Audio Class 2.0 Status/Interrupt endpoint disabled by default
    (enabled when SPDIF/ADAT receive enabled)
  * CHANGE:     DFU/Flash code simplified
  * RESOLVED:   (Minor) Fixed issue where buffering can lock up on sample
    frequency change if in overflow (#10897)
  * RESOLVED:   (Minor) XN files updated to avoid deprecation warnings from
    tools
  * RESOLVED:   (Major) Fixed issue where installation of the first upgrade
    image is successful but subsequent upgrades fail (Design Advisory X2035A)

  * Changes to dependencies:

    - sc_adat: Added dependency 1.0.0

      + Initial release

    - sc_i2c: Added dependency 1.0.0

    - sc_spdif: Added dependency 1.0.0

    - sc_usb: Added dependency 1.0.0

      + Initial release

    - sc_usb_audio: Added dependency 1.0.0

    - sc_xud: Added dependency 1.0.0

      + Initial stand-alone release


Legacy release history
----------------------

(Note: USB Audio version numbers unified across all products at this point)

Previous L1 Firmware Releases
+++++++++++++++++++++++++++++

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
	- ADDED:      MIDI functionality
    - CHANGE:     Buffering re-factored

1.7.0
-----
    - RESOLVED:   Buffering fixes for non-intel USB chipsets

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
+++++++++++

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
+++++++++++++++++++++++++++++

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
                  (Port buffers enabled on USB clock port)    - Initial Alpha release
    - 10 channel input/output (8 chan DAC, 6 chan ADC, 2 chan S/PDIF tx)
    - Master/channel volume/mute controls


L2 Hardware
+++++++++++

1.2.0
-----
    - Update for coax in, coax out cap & minor tidyup

1.1.0
-----
    - Initial production

1.0.0
-----
    - Pre-production


