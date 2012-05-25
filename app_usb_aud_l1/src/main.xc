/**
 * @file    main.xc
 * @brief   XMOS L2 USB 2.0 Audio 2.0 Reference Design.  Top level.
 * @author  Ross Owen, XMOS Semiconductor Ltd 
 */                               

#include <syscall.h>
#include <platform.h>
#include <xs1.h>
#include <xclib.h>
#include <print.h>

#include "xud.h"                 /* XMOS USB Device Layer defines and functions */
#include "usb.h"                 /* Defines from the USB 2.0 Specification */

#include "devicedefines.h"      /* Device specific defines */  
#include "endpoint0.h"
#include "usb_buffer.h"
#include "port32A.h"
#include "usb_midi.h"

void audio(chanend c_mix_out, chanend?, chanend?) ;

/* Audio I/O */
on stdcore[0] : buffered out port:32 p_i2s_dac[1] = {PORT_I2S_DAC_DATA};
on stdcore[0] : buffered in port:32 p_i2s_adc[1]  = {PORT_I2S_ADC_DATA}; 
on stdcore[0] : buffered out port:32 p_lrclk      = PORT_I2S_LRCLK;
on stdcore[0] : buffered out port:32 p_bclk       = PORT_I2S_BCLK;
on stdcore[0] : port p_mclk                       = PORT_MCLK_IN;

on stdcore[0] : buffered out port:32 p_spdif_tx   = PORT_SPDIF_OUT;

on stdcore[0] :in  port p_for_mclk_count          = XS1_PORT_4D;

/* USB Reset port */
on stdcore[0] : out port p_usb_rst                = XS1_PORT_32A;

#ifdef MIDI
on stdcore[0] : port p_midi_tx                    = XS1_PORT_1J;
on stdcore[0] : port p_midi_rx                    = XS1_PORT_1K;
#endif

/* Clock blocks */
on stdcore[0] : clock    clk_midi                 = XS1_CLKBLK_1;
on stdcore[0] : clock    clk_audio_mclk           = XS1_CLKBLK_2;     /* Master clock */
on stdcore[0] : clock    clk_audio_bclk           = XS1_CLKBLK_3;     /* Bit clock */
on stdcore[0] : clock    clk                      = XS1_CLKBLK_4;     /* USB clock */
on stdcore[0] : clock    clk_mst_spd              = XS1_CLKBLK_5;

void decouple(chanend, chanend?, chanend?);

void mixer(chanend, chanend, chanend );

void spdif_transmitter(buffered out port:32 p, chanend c_in);

/* Endpoint type tables for XUD */
XUD_EpType epTypeTableOut[NUM_EP_OUT] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE, 
                                            XUD_EPTYPE_ISO, 
                                            XUD_EPTYPE_BUL,
                                            XUD_EPTYPE_DIS};

XUD_EpType epTypeTableIn[NUM_EP_IN] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE,
                                            XUD_EPTYPE_ISO, 
                                            XUD_EPTYPE_ISO,
                                            XUD_EPTYPE_BUL,
                                            XUD_EPTYPE_BUL};
#define FAST_MODE 0

void thread_speed()
{
#if (FAST_MODE)
    set_thread_fast_mode_on();
#else
    set_thread_fast_mode_off();
#endif
}

int main()
{
    chan c_sof;
    chan c_xud_out[NUM_EP_OUT];              /* Endpoint channels for XUD */
    chan c_xud_in[NUM_EP_IN];
    chan c_aud_ctl;
    chan c_mix_out;
#ifdef MIDI
    chan c_midi;
#endif

#ifdef TEST_MODE_SUPPORT
#warning Building with test mode support
    chan c_usb_test;
#else
#define c_usb_test null
#endif

    set_port_clock(p_for_mclk_count, clk_audio_mclk);

    par 
    {
        /* USB Interface */
#if (AUDIO_CLASS==2) 
        XUD_Manager(c_xud_out, NUM_EP_OUT, c_xud_in, NUM_EP_IN, 
                  c_sof, epTypeTableOut, epTypeTableIn, p_usb_rst, 
                  clk, 1, XUD_SPEED_HS, c_usb_test);  
#else
        XUD_Manager(c_xud_out, NUM_EP_OUT, c_xud_in, NUM_EP_IN, 
                  c_sof, epTypeTableOut, epTypeTableIn, p_usb_rst, 
                  clk, 1, XUD_SPEED_FS, c_usb_test);  
#endif
        
        /* Endpoint 0 */
        {
            thread_speed();
            Endpoint0( c_xud_out[0], c_xud_in[0], c_aud_ctl, null,null, c_usb_test);
        }

        /* Buffer / EP Man */
        {
            thread_speed();
            buffer(c_xud_out[1], c_xud_in[2], c_xud_in[1],
                c_xud_out[2], c_xud_in[3], c_xud_in[4],
                c_sof, c_aud_ctl, p_for_mclk_count);
        }

        {
            thread_speed();
            decouple(c_mix_out,
#ifdef MIDI
               c_midi,
#else
               null,
#endif
               null);
        }

        {
            thread_speed();
            /* Audio I/O (pars additional S/PDIF TX thread) */ 
            audio(c_mix_out, null, null);
        }
#ifdef MIDI
        {
            thread_speed();
            usb_midi(p_midi_rx, p_midi_tx, clk_midi, c_midi, 0, null, null, null, null);
        }
#endif
    }

    return 0;
}



