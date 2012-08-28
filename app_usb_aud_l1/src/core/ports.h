#ifndef _PORTS_H_
#define _PORTS_H_

/* Port map for L1 USB Audio Reference Design Board */

/* Standard ports supported in USB Audio frame work */
#define PORT_I2S_BCLK                       XS1_PORT_1A
#define PORT_I2S_LRCLK                      XS1_PORT_1C
#define PORT_I2S_DAC0                       XS1_PORT_1D
#define PORT_I2S_ADC0                       XS1_PORT_1I
#define PORT_MIDI_OUT                       XS1_PORT_1J
#define PORT_MIDI_IN                        XS1_PORT_1K
#define PORT_SPDIF_OUT                      XS1_PORT_1L
#define PORT_MCLK_IN                        XS1_PORT_1M
#define PORT_MCLK_COUNT                     XS1_PORT_16B
#define PORT_USB_RESET                      XS1_PORT_32A

/* Additional ports used in this application instance */

/* For this design the USB reset port is on port 32A, this port is also used for some GPIO items.\
 * We can't simply declare it here as we would like to i.e:
 *
 * on stdcore[0] : out port p_gpio = XS1_PORT_32A;
 * 
 * since the compiler would issue an error.  We'll use some assembly magic to work around this.
 */
#endif 
