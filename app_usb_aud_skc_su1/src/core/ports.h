
#ifndef _PORTS_H_
#define _PORTS_H_


/* Standard ports supported in USB Audio framework */

#if 1
/* Port map for Audio Slice (1v0) on SU1 core board */
#define PORT_I2S_BCLK            XS1_PORT_1A
#define PORT_I2S_DAC1            XS1_PORT_1B
#define PORT_I2S_LRCLK           XS1_PORT_1C
#define PORT_I2S_DAC0            XS1_PORT_1D
#define PORT_MCLK_IN             XS1_PORT_1E
#define PORT_MIDI_IN             XS1_PORT_1F
#define PORT_SPDIF_OUT           XS1_PORT_1G
#define PORT_I2S_ADC0            XS1_PORT_1I
#define PORT_I2S_ADC1            XS1_PORT_1L
#define PORT_MIDI_OUT            XS1_PORT_8D
#define PORT_MCLK_COUNT          XS1_PORT_16B
#endif

#if 0
/* Port map for Audio Slice (1v1) on SU1 core board */
#define PORT_I2S_BCLK            XS1_PORT_1A
#define PORT_SPDIF_OUT           XS1_PORT_1B
#define PORT_I2S_DAC1            XS1_PORT_1C
#define PORT_I2S_DAC0            XS1_PORT_1D
#define PORT_MCLK_IN             XS1_PORT_1E
#define PORT_MIDI_IN             XS1_PORT_1F
#define PORT_I2S_ADC0            XS1_PORT_1G
#define PORT_I2S_LRCLK           XS1_PORT_1I
#define PORT_I2S_ADC1            XS1_PORT_1L
#define PORT_MIDI_OUT            XS1_PORT_8D
#define PORT_MCLK_COUNT          XS1_PORT_16B
#endif

/* Additional ports used in this application instance */
on stdcore[0] : out port p_gpio = XS1_PORT_4C;
on stdcore[0] : port p_i2c      = XS1_PORT_4D;

#endif
