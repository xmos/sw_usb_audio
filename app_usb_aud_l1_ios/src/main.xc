/**
 * @file    main.xc
 * @brief   XMOS L2 USB 2.0 Audio 2.0 Reference Design.  Top level.
 * @author  Ross Owen, XMOS Semiconductor Ltd 
 * @version 1.4
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
#include "expansion.h"
#include "usb_midi.h"

#include "iAP.h"

void audio(chanend c_mix_out, chanend?, chanend?);

/* Audio I/O */
on stdcore[0] : buffered out port:32 p_i2s_dac[1] = {XS1_PORT_1D};
on stdcore[0] : buffered in port:32 p_i2s_adc[1] = {XS1_PORT_1M}; 
on stdcore[0] : buffered out port:32 p_lrclk      = XS1_PORT_1C;
on stdcore[0] : buffered out port:32 p_bclk       = XS1_PORT_1A;
on stdcore[0] : port p_mclk                       = XS1_PORT_1L;

on stdcore[0] : buffered out port:32 p_spdif_tx   = XS1_PORT_1K;

on stdcore[0] :in  port p_for_mclk_count          = XS1_PORT_1E;
 
/* USB Reset port */
on stdcore[0] : out port p_usb_rst                = XS1_PORT_32A;

on stdcore[0] : port p_i2c_scl                    = XS1_PORT_1I;
on stdcore[0] : port p_i2c_sda                    = XS1_PORT_1J;

#define p_midi_tx p_i2c_scl
#define p_midi_rx p_i2c_sda

/* Clock blocks */
on stdcore[0] : clock    clk_midi                 = XS1_CLKBLK_1;     
on stdcore[0] : clock    clk_audio_mclk           = XS1_CLKBLK_2;     /* Master clock */
on stdcore[0] : clock    clk_audio_bclk           = XS1_CLKBLK_3;     /* Bit clock */
on stdcore[0] : clock    clk                      = XS1_CLKBLK_4;     /* USB clock */
on stdcore[0] : clock    clk_mst_spd              = XS1_CLKBLK_5;

timer i2ctimer;

void decouple(chanend, chanend?, chanend?
#ifdef IAP
, chanend?
#endif
);

// This prevents all of the shutdown code being compiled in, saving about 2K
void __libc_done() { };
void _exit_unlocked() { };

void mixer(chanend, chanend, chanend );

void spdif_transmitter(buffered out port:32 p, chanend c_in);

/* Endpoint type tables for XUD */
XUD_EpType epTypeTableOut[NUM_EP_OUT] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE, 
                                            XUD_EPTYPE_ISO, 
                                            XUD_EPTYPE_BUL,
                                            XUD_EPTYPE_BUL
};

XUD_EpType epTypeTableIn[NUM_EP_IN] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE,
                                            XUD_EPTYPE_ISO, 
                                            XUD_EPTYPE_ISO,
                                            XUD_EPTYPE_BUL,
                                            XUD_EPTYPE_BUL,
                                            XUD_EPTYPE_BUL | XUD_STATUS_ENABLE,  /* iAP bulk EP */
                                            XUD_EPTYPE_INT | XUD_STATUS_ENABLE}; /* iAP int EP */
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
#ifdef IAP
    chan c_iap;
#endif

    set_port_clock(p_for_mclk_count, clk_audio_mclk);

#ifdef IO_EXPANSION
    expansion_io_init();
#endif
    set_clock_on(clk);
    set_clock_ref(clk);
    set_port_clock(p_usb_rst, clk);
    start_clock(clk);

    port32A_set(P32A_USB_RST | P32A_ACC_DET_ID_EN);

    par {
      /* USB Interface */

#if (AUDIO_CLASS==2) 
      XUD_Manager(c_xud_out, NUM_EP_OUT, c_xud_in, NUM_EP_IN, 
                  c_sof, epTypeTableOut, epTypeTableIn, null, 
                  clk, 1, XUD_SPEED_HS, null);  
#else
      XUD_Manager(c_xud_out, NUM_EP_OUT, c_xud_in, NUM_EP_IN, 
                  c_sof, epTypeTableOut, epTypeTableIn, null, 
                  clk, 1, XUD_SPEED_FS, null);  
#endif
        
      /* Endpoint 0 */
      {
          thread_speed();
      Endpoint0( c_xud_out[0], c_xud_in[0], c_aud_ctl, null, null, null);
        }


      /* Buffer / EP Man */
      {
          thread_speed();
      buffer(c_xud_out[1], c_xud_in[2], c_xud_in[1],
             c_xud_out[2], c_xud_in[3],
#ifdef IAP
            c_xud_out[3], c_xud_in[5], c_xud_in[6], // from_host, to_host, to_host_int
#endif
             c_xud_in[4],
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
               null
#ifdef IAP
               ,c_iap
#endif
);
    }
    {
        thread_speed();
      /* Audio I/O (pars additional S/PDIF TX thread) */ 
      audio(c_mix_out, null, null);
}
#if defined MIDI || defined IAP
        {
            thread_speed();
#ifdef MIDI
            usb_midi(p_midi_rx, p_midi_tx, clk_midi, c_midi, 0, c_iap, null, null, null);
#else
            iAP(c_iap, null);
#endif
        }
#endif
    }

    return 0;
}
