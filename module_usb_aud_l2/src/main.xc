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
#include <stdio.h>

#include "xud.h"                 /* XMOS USB Device Layer defines and functions */
#include "usb.h"                 /* Defines from the USB 2.0 Specification */
// Added
#include "iic.h"
#ifdef IAP
#include "coProcessor.h"
#include "iAP.h"
#include "i2c_thread.h"
#endif

#include "decouple.h"

#include "customdefines.h"
#include "devicedefines.h"      /* Device specific defines */  
#include "endpoint0.h"
#include "usb_buffer.h"
#include "SpdifReceive.h"      /* module_spdif_rx */ 
#include "usb_midi.h"
#include "adatreceiver.h"
#include "audio.h"

void clockGen (streaming chanend c_spdif_rx, chanend c_adat_rx, out port p, chanend, chanend, chanend);
void mixer(chanend, chanend, chanend);

/* Cores */
#define CORE_USB                    0
#define CORE_AUD                    1

/* Core 0 */
#define PORT_USB_RST                XS1_PORT_1M       
#define PORT_PLL_CLK                XS1_PORT_4E         /* Clk Output to PLL */

/* Core 1 */
#define PORT_COD_CLK_BIT            XS1_PORT_1I         /* Bit clock */
#define PORT_COD_CLK_LR             XS1_PORT_1E         /* LR clock */
#define PORT_I2C_SCL                XS1_PORT_1D
#define PORT_I2C_SDA                XS1_PORT_1C     

#define PORT_COD_DAC_0              XS1_PORT_1M
#define PORT_COD_DAC_1              XS1_PORT_1F
#define PORT_COD_DAC_2              XS1_PORT_1H
#define PORT_COD_DAC_3              XS1_PORT_1N

#define PORT_COD_ADC_0              XS1_PORT_1G
#define PORT_COD_ADC_1              XS1_PORT_1A
#define PORT_COD_ADC_2              XS1_PORT_1B

#define PORT_COD_CLK_MAS            XS1_PORT_1L

on stdcore[CORE_USB] : buffered in port:4 p_spdif_rx    = XS1_PORT_1K; /* K: coax, J: optical */
on stdcore[CORE_USB] : buffered in port:32 p_adat_rx    = XS1_PORT_1J; /* K: coax, J: optical */
on stdcore[CORE_USB] : out port p_usb_rst               = PORT_USB_RST;
on stdcore[CORE_USB] : in port p_for_mclk_count         = XS1_PORT_32A;
on stdcore[CORE_USB] : in port p_mclk_too               = XS1_PORT_1L;
on stdcore[CORE_AUD] : out port p_pll_clk               = PORT_PLL_CLK;
#ifdef CODEC_SLAVE 
on stdcore[CORE_AUD] : buffered out port:32 p_lrclk     = PORT_COD_CLK_LR;
on stdcore[CORE_AUD] : buffered out port:32 p_bclk      = PORT_COD_CLK_BIT;
#else
on stdcore[CORE_AUD] : in port p_lrclk                  = PORT_COD_CLK_LR;
on stdcore[CORE_AUD] : in port p_bclk                   = PORT_COD_CLK_BIT;
#endif
on stdcore[CORE_AUD] : port p_mclk                      = PORT_COD_CLK_MAS;
on stdcore[CORE_AUD] : out port p_aud_cfg               = XS1_PORT_4A;
on stdcore[CORE_AUD] : port p_i2c_scl                   = PORT_I2C_SCL;     // 2-wire configuration interface.
on stdcore[CORE_AUD] : port p_i2c_sda                   = PORT_I2C_SDA;   
on stdcore[CORE_AUD] : buffered out port:32 p_spdif_tx  = XS1_PORT_1K;      // K: coax, J: optical
on stdcore[CORE_AUD] : port p_midi_tx                   = XS1_PORT_1O;
on stdcore[CORE_AUD] : port p_midi_rx                   = XS1_PORT_1P;
on stdcore[CORE_AUD] : buffered out port:32 p_i2s_dac[I2S_WIRES_DAC] = {PORT_COD_DAC_0, PORT_COD_DAC_1, PORT_COD_DAC_2, PORT_COD_DAC_3};
on stdcore[CORE_AUD] : buffered in port:32 p_i2s_adc[I2S_WIRES_ADC]  = {PORT_COD_ADC_0, PORT_COD_ADC_1, PORT_COD_ADC_2};

/* Clock blocks */
on stdcore[CORE_USB] : clock    clk_adat_rx             = XS1_CLKBLK_1;
on stdcore[CORE_USB] : clock    clk_spi                 = XS1_CLKBLK_2;   
on stdcore[CORE_USB] : clock    clk                     = XS1_CLKBLK_3;     /* USB clock */
on stdcore[CORE_USB] : clock    clk_spd_rx              = XS1_CLKBLK_4;
on stdcore[CORE_USB] : clock    clk_master_too          = XS1_CLKBLK_5;     /* Master clock on USB core */

on stdcore[CORE_AUD] : clock    clk_audio_mclk          = XS1_CLKBLK_1;     /* Master clock */
on stdcore[CORE_AUD] : clock    clk_audio_bclk          = XS1_CLKBLK_2;     /* Bit clock */
on stdcore[CORE_AUD] : clock    clk_midi                = XS1_CLKBLK_3;   
on stdcore[CORE_AUD] : clock    clk_mst_spd             = XS1_CLKBLK_4;

on stdcore[CORE_AUD] : out port p_led                   = XS1_PORT_8B;
on stdcore[CORE_AUD] : out port p_gpio                  = XS1_PORT_4F;

/* Endpoint type tables for XUD */
XUD_EpType epTypeTableOut[NUM_EP_OUT] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE, 
                                            XUD_EPTYPE_ISO, // AUDIO
                                            XUD_EPTYPE_BUL, // MIDI
#ifdef IAP
                                            XUD_EPTYPE_BUL // iAP Bulk out
#endif
};

XUD_EpType epTypeTableIn[NUM_EP_IN] = { XUD_EPTYPE_CTL | XUD_STATUS_ENABLE,
                                            XUD_EPTYPE_ISO, 
                                            XUD_EPTYPE_ISO,
                                            XUD_EPTYPE_BUL, // MIDI
                                            XUD_EPTYPE_BUL, // AS interrupt endpoint
#ifdef IAP
                                            XUD_EPTYPE_BUL | XUD_STATUS_ENABLE, // iAP Bulk in 
                                            XUD_EPTYPE_INT | XUD_STATUS_ENABLE// iAP Int in
#endif
};

/** For testing, this define can turn core 0 threads onto "fast mode".
    This is to test worst case control flow paths for performance.
*/  
#if 0
#define CORE_0_FAST_MODE set_thread_fast_mode_off();
#else
#define CORE_0_FAST_MODE set_thread_fast_mode_on();
#endif

on stdcore[1] : timer anothertimer;

int main()
{
    chan c_sof;
    
    chan c_xud_out[NUM_EP_OUT];             /* Endpoint channels for XUD */
    chan c_xud_in[NUM_EP_IN];
    
    chan c_aud_ctl;
    chan c_mix_ctl;
    chan c_clk_ctl;
    
    chan c_mix_out;

    chan c_dig_rx;
    chan c_del_out;
    streaming chan c_spdif_rx;
    chan c_adat_rx;  // CT_END after each sample
#ifdef MIDI
    chan c_midi;
#else
#define c_midi null
#endif

#ifdef IAP
    chan c_iap;
    chan c_i2c_copro;
    chan c_config; /* From audio thread to i2c thread */
#else
#define c_iap null
#define c_i2c_copro null
#define c_config null
#endif

    chan c_clk_int;

    par
    {
        /* Core 0 */
        /* USB Interface */
        on stdcore[0] : 
        {
            XUD_Manager(c_xud_out, NUM_EP_OUT, c_xud_in, NUM_EP_IN, 
                c_sof, epTypeTableOut, epTypeTableIn, p_usb_rst, clk, 1, XUD_SPEED_HS, null);  
        }
        
        /* Endpoint 0 */
        on stdcore[0] : 
        {
            Endpoint0( c_xud_out[0], c_xud_in[0], c_aud_ctl, c_mix_ctl, c_clk_ctl,null);
        }

        /* Buffer / EP Man */
        on stdcore[0] :
        {
            set_thread_fast_mode_on();                         
            configure_clock_src(clk_master_too, p_mclk_too);
            set_port_clock(p_for_mclk_count, clk_master_too);
            start_clock(clk_master_too);

            buffer(c_xud_out[1], c_xud_in[2], c_xud_in[1], 
                c_xud_out[2], c_xud_in[3],
#ifdef IAP
                c_xud_out[3], c_xud_in[5], c_xud_in[6],
#endif
#if defined(SPDIF_RX) || defined(ADAT_RX)
                c_xud_in[4],
#else
                null,
#endif



                c_sof,  c_aud_ctl, p_for_mclk_count);
        }

        on stdcore[0] : 
        {
            decouple(c_mix_out, c_midi, c_clk_int
#ifdef IAP
            , c_iap
#endif
            );
        }

#ifdef SPDIF_RX
        on stdcore[0] :
        { 
            set_thread_fast_mode_on();                         
            SpdifReceive(p_spdif_rx, c_spdif_rx, 1, clk_spd_rx);
        }
#endif
#ifdef ADAT_RX
        on stdcore[0] : 
        {
            set_thread_fast_mode_on();                         
            set_port_clock(p_adat_rx, clk_adat_rx);
            start_clock(clk_adat_rx);
            while (1)
            {
				adatReceiver48000(p_adat_rx, c_adat_rx);
				adatReceiver44100(p_adat_rx, c_adat_rx);
			}
        }
#endif

#ifdef MIXER
        /* Core 1 */
        on stdcore[1] : 
        {   
            mixer(c_mix_out, c_del_out, c_mix_ctl);
        }
#endif

        /* Audio I/O (pars additional S/PDIF TX thread) */
        on stdcore[1] : 
        {   
            audio(c_del_out, c_dig_rx, c_config);
        }

#ifdef IAP
        on stdcore[1] : 
        {   
            i2c_thread(c_config, c_i2c_copro, p_i2c_scl, p_i2c_sda);
        }
#endif

        on stdcore[1] : 
        {   
            clockGen(c_spdif_rx, c_adat_rx, p_pll_clk, c_dig_rx, c_clk_ctl, c_clk_int);
        }

#if defined MIDI || defined IAP 
#ifdef MIDI
        on stdcore[1] : usb_midi(p_midi_rx, p_midi_tx, clk_midi, c_midi, 0, c_iap, c_i2c_copro, null, null);
#else
        on stdcore[1] : iAP(c_iap, c_i2c_copro);
#endif
#endif
 
    }

    return 0;
}



