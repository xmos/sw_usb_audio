XMOS XS1-L8 USB Audio 2.0 Reference Design (app_usb_aud_l1)
===========================================================

:maintainer: Ross Owen
:scope: General Use
:description: USB Audio for L1 USB Audio board
:keywords: USB, Audio, MFA
:boards: XR-USB-AUDIO-2.0

Overview
........

The firmware provides a high-speed USB audio device designed to be compliant to version 2.0 of the USB Audio Class Specification.

When connected via a full-speed hub the device falls back to operate at Audio 1.0 at full-speed.  A different PID is used to 
avoid Windows driver caching issues.

Additionally, build options are provided for Audio Class 1.0.  To remain compliant this causes the device to run at full-speed.

When running at full-speed sample-frequency restrictions are enforced to ensure fitting within the band-width restrictions of 
full-speed USB.

The firmware provides stereo input and output via I2S and stereo output via S/PDIF.  Build options are provided to enable/disable 
input and output functionality.

Key Features
............

The app_usb_aud_l1 application is designed to run on the XMOS USB Audio 2.0 References Design board
(part number xr-usb-audio-2.0).  This application used the XMOS USB Audio framework. Key features 
of this application are as follows: 

- USB Audio Class 2.0 Compliant  

- Fully Asynchronous operation

- Stereo analogue input and output

- S/PDIF Output

- Supports the following sample frequencies: 44.1, 48, 88.2, 96, 176.4*, 192kHz

- Field firmware upgrade compliant to the USB Device Firmware Upgrade (DFU) Class Specification

* S/PDIF Output at 176.4kHz not supported due to mclk requirements

Known Issues
............

See README in sw_usb_audio for general issues.

- CODEC (CS4270) auto-mute/soft-ramp feature can cause volume ramp at start of playback.  These features cannot be disabled on the reference board since CODEC is used in Hardware Mode (i.e. not configured using I2C)

- No XMOS Link for XScope available on the board

- The board has a 11.289MHz master clock source (oscillator) for 44.1kHz family of sample frequencies. S/PDIF Tx operation at 176.4kHz is therefore not supported due to the 2 x MCLK requirement. I2S functionality at this rate is unaffected.

Please also note:  

Remedying the lack 176.4kHz S/PDIF support The CODEC is configured in hardware mode.  The scheme used uses a single pin (MDIV2) to indicate 256 or 512fs.  This same line is used on the board to control master-clock selection.  In 256fs mode with a 22.578 master-clock 44.1 cannot be achieved by the CODEC (88.2kHz and 176.4kHz should operate as expected).

A modification could be made in order to add full functionality. i.e. MDIV2 high (to always indicate 512fs). In addition the line from this to clock-selection input must be broken in order for the clock-selection to still operate.  The master-clock frequency defines should also be suitably modified.

Support
.......

For all support issues please visit http://www.xmos.com/support


