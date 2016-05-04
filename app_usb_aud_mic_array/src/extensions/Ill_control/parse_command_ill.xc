#include <print.h>
#include <stdio.h>
#include <stdlib.h>
#include "control.h"
#include "xvsm_support.h"
#include "parse_command_ill.h"
#include "control_module_ids.h"


//#define DBG(x) x
#define DBG(x)

#define debug_printf(x) printf(x)

/* Old Illusonic control protocol is ASCII based so do conversion first */
void asciify(uint8_t buffer[], int num_bytes_read, int &argc, int argv[IVL_MAX_NUM_MODULE_ARGS])
{
    DBG(printstr("control : ("); printint(num_bytes_read); printstr(") :");printstrln(buffer);)

    argc = 0;
    argv[argc++] = atoi(buffer);
    for (int i = 0; i < num_bytes_read; ++i) {
        if (buffer[i] == ':') {
            if (i + 1 < num_bytes_read) {
                argv[argc++] = atoi(&buffer[i + 1]);
                if (argc > IVL_MAX_NUM_MODULE_ARGS) {
                    break;
                }
            }
        }
    }
}



/*
 * Accepts messages of the form:
 * "<moduleID> <E> <enabled>"
 * "<moduleID> <U> <gain>"
 *
 * Returns 0 = fail, 1 = success
 */
//int cntrlAudioProcess(ilvlState &state, int argc, int argv[IVL_MAX_NUM_MODULE_ARGS])
int cntrlAudioProcess(il_voice_rtcfg_t &ilv_rtcfg, il_voice_cfg_t &ilv_cfg,  il_voice_diagnostics_t &ilv_diag, int argc, int argv[IVL_MAX_NUM_MODULE_ARGS])
{
  int err;
  int param;

  DBG(printstr("cntrlAudioProcess:: ");)
  DBG(for (unsigned int i = 0; i < argc; ++i) {printint(argv[i]); printstr(" ");} printstr("\n");)

  if ((argc != 3) || ((argv[0] & 0xfffff000) != IVL_BASE_MODULE_ID)) {            // All commands have 3 parameters
    return 0;
  }

  if (argv[0] == IVL_BASE_MODULE_ID) {
    switch (argv[1]) {
      case 'R':
        il_voice_reset_audio();
        il_voice_get_default_cfg(ilv_cfg, ilv_rtcfg);
        err = il_voice_init(ilv_cfg, ilv_rtcfg);
        if (err) {
            debug_printf("cntrlAudioProcess:: Error: Failed to initialize voice engine\n");
            _Exit(1);
        }
        DBG(printstrln("cntrlAudioProcess:: il_voice_reset_audio() Done");)
        return 1;
    }
  }
  else if (argv[0] == IVL_BYPASS_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= BYPASS_ON_MIN) && (param <= BYPASS_ON_MAX)) {
          ilv_rtcfg.bypass_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.bypass_on : "); printintln(ilv_rtcfg.bypass_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_INIT_MODULE_ID) {
    switch (argv[1]) {
      case 'I':
        param = argv[2];
        if ((param >= MIC_GAIN_MIN) && (param <= MIC_GAIN_MAX)) {
          il_voice_update_mic_gain(param);
          DBG(printstr("cntrlAudioProcess:: il_voice_update_mic_gain : "); printintln(param);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'O':
        param = argv[2];
        if ((param >= SPK_GAIN_MIN) && (param <= SPK_GAIN_MAX)) {
          il_voice_update_spk_gain(param);
          DBG(printstr("cntrlAudioProcess:: il_voice_update_spk_gain : "); printintln(param);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_MIC_MODULE_ID) {
    switch (argv[1]) {
      case 'S':
        param = argv[2];
        if ((param >= MIC_SHIFT_MIN) && (param <= MIC_SHIFT_MAX)) {
          ilv_rtcfg.mic_shift = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.mic_shift : "); printintln(ilv_rtcfg.mic_shift);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_BEAM_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.bf_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.bf_on : "); printintln(ilv_rtcfg.bf_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'D':
        param = argv[2];
        if ((param >= 0) && (param <= BF_DIRECTION_MAX)) {
          ilv_rtcfg.bf_direction = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.bf_direction : "); printintln(ilv_rtcfg.bf_direction);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;

      case 'F':
        param = argv[2];
        if ((param >= 0) && (param <= BF_FOCUS_MAX)) {
          ilv_rtcfg.bf_focus = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.bf_focus : "); printintln(ilv_rtcfg.bf_focus);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;


      case 'G':
        param = argv[2];
        if ((param >= BF_DIFF_GAIN_MIN) && (param <= BF_DIFF_GAIN_MAX)) {
          ilv_rtcfg.bf_diffgain_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.bf_diffgain_dB : "); printintln(ilv_rtcfg.bf_diffgain_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_NOISE_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.ns_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.ns_on : "); printintln(ilv_rtcfg.ns_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'A':
        param = argv[2];
        if ((param >= NS_ATTEN_MIN) && (param <= NS_ATTEN_MAX)) {
          ilv_rtcfg.ns_attlimit_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.ns_attlimit_dB : "); printintln(ilv_rtcfg.ns_attlimit_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_DEREV_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.rvb_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.rvb_on : "); printintln(ilv_rtcfg.rvb_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'A':
        param = argv[2];
        if ((param >= RVB_ATTEN_MIN) && (param <= RVB_ATTEN_MAX)) {
          ilv_rtcfg.rvb_attlimit_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.rvb_attlimit_dB : "); printintln(ilv_rtcfg.rvb_attlimit_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_AEC_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.aec_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_on : "); printintln(ilv_rtcfg.aec_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'D':
        param = argv[2];
        if ((param >= AEC_DELAY_MIN) && (param <= AEC_DELAY_MAX)) {
          ilv_rtcfg.aec_delay_ms = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_delay_ms : "); printintln(ilv_rtcfg.aec_delay_ms);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'S':
        param = argv[2];
        if ((param >= AEC_STRENGTH_MIN) && (param <= AEC_STRENGTH_MAX)) {
          ilv_rtcfg.aec_strength = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_strength : "); printintln(ilv_rtcfg.aec_strength);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'N':
        param = argv[2];
        if ((param >= AEC_NONLIN_MIN) && (param <= AEC_NONLIN_MAX)) {
          ilv_rtcfg.aec_nonlin = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_nonlin : "); printintln(ilv_rtcfg.aec_nonlin);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;

      case 'O':
        param = argv[2];
        if ((param >= AEC_LECHOFF_MIN) && (param <= AEC_LECHOFF_MIN)) {
          ilv_rtcfg.aec_lecho_offset_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_lecho_offset_dB : "); printintln(ilv_rtcfg.aec_lecho_offset_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'L':
        param = argv[2];
        if ((param >= AEC_LECHTIME_MIN) && (param <= AEC_LECHTIME_MAX)) {
          ilv_rtcfg.aec_lecho_len_ms = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_lecho_len_ms : "); printintln(ilv_rtcfg.aec_lecho_len_ms);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'F':
        param = argv[2];
        if ((param >= AEC_FTHR_MIN) && (param <= AEC_FTHR_MAX)) {
          ilv_rtcfg.aec_force_thr_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_force_thr_dB : "); printintln(ilv_rtcfg.aec_force_thr_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'T':
        param = argv[2];
        if ((param >= AEC_NTHR_MIN) && (param <= AEC_NTHR_MAX)) {
          ilv_rtcfg.aec_noise_thr_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_noise_thr_dB : "); printintln(ilv_rtcfg.aec_noise_thr_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'H':
        param = argv[2];
        if ((param >= AEC_DTTHR_MIN) && (param <= AEC_DTTHR_MAX)) {
          ilv_rtcfg.aec_dt_thr_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_dt_thr_dB : "); printintln(ilv_rtcfg.aec_dt_thr_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'R':
        param = argv[2];
        if ((param >= AEC_DTREL_MIN) && (param <= AEC_DTREL_MAX)) {
          ilv_rtcfg.aec_dt_release_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_dt_release_dB : "); printintln(ilv_rtcfg.aec_dt_release_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'A':
        param = argv[2];
        if ((param >= AEC_DTATT_MIN) && (param <= AEC_DTATT_MAX)) {
          ilv_rtcfg.aec_dt_att_limit_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_dt_att_limit_dB : "); printintln(ilv_rtcfg.aec_dt_att_limit_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'P':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.aec_no_adapt = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_no_adapt : "); printintln(ilv_rtcfg.aec_no_adapt);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'G':
        param = argv[2];
        if ((param >= AEC_IGAIN_MIN) && (param <= AEC_IGAIN_MAX)) {
          ilv_rtcfg.aec_init_gain_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.aec_init_gain_dB : "); printintln(ilv_rtcfg.aec_init_gain_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_AGC_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.agc_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.agc_on : "); printintln(ilv_rtcfg.agc_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'G':
        param = argv[2];
        if ((param >= AGC_IGAIN_MIN) && (param <= AGC_IGAIN_MAX)) {
          ilv_rtcfg.agc_init_gain_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.agc_init_gain_dB : "); printintln(ilv_rtcfg.agc_init_gain_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'T':
        param = argv[2];
        if ((param >= AGC_TGAIN_MIN) && (param <= AGC_TGAIN_MAX)) {
          ilv_rtcfg.agc_target_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.agc_target_dB : "); printintln(ilv_rtcfg.agc_target_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_EQ_MODULE_ID) {
    switch (argv[1]) {
      case 'M':
        param = argv[2];
        if ((param >= MIC_EQ_INDEX_MIN) && (param <= MIC_EQ_INDEX_MAX)) {
          ilv_rtcfg.mic_eq_index = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.mic_eq_index : "); printintln(ilv_rtcfg.mic_eq_index);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'S':
        param = argv[2];
        if ((param >= SPK_EQ_INDEX_MIN) && (param <= SPK_EQ_INDEX_MAX)) {
          ilv_rtcfg.spk_eq_index = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_eq_index : "); printintln(ilv_rtcfg.spk_eq_index);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_SPK_LIM_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.spk_limiter_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_limiter_on : "); printintln(ilv_rtcfg.spk_limiter_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'T':
        param = argv[2];
        if ((param >= SPK_LIM_THR_MIN) && (param <= SPK_LIM_THR_MAX)) {
          ilv_rtcfg.spk_limiter_thr_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_limiter_thr_dB : "); printintln(ilv_rtcfg.spk_limiter_thr_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_SPK_CMP_MODULE_ID) {
    switch (argv[1]) {
      case 'E':
        param = argv[2];
        if ((param >= 0) && (param <= 1)) {
          ilv_rtcfg.spk_compr_on = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_compr_on : "); printintln(ilv_rtcfg.spk_compr_on);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'T':
        param = argv[2];
        if ((param >= SPK_COMP_THR_MIN) && (param <= SPK_COMP_THR_MAX)) {
          ilv_rtcfg.spk_compr_thr_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_compr_thr_dB : "); printintln(ilv_rtcfg.spk_compr_thr_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'G':
        param = argv[2];
        if ((param >= SPK_COMP_GAIN_MIN) && (param <= SPK_COMP_GAIN_MAX)) {
          ilv_rtcfg.spk_compr_gain_dB = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_compr_gain_dB : "); printintln(ilv_rtcfg.spk_compr_gain_dB);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      case 'R':
        param = argv[2];
        if ((param >= SPK_COMP_RATIO_MIN) && (param <= SPK_COMP_RATIO_MAX)) {
          ilv_rtcfg.spk_compr_ratio = param;
          DBG(printstr("cntrlAudioProcess:: ilv_rtcfg.spk_compr_ratio : "); printintln(ilv_rtcfg.spk_compr_ratio);)
        }
        else {              // Invalid parameter
          return 0;
        }
        break;
      default:              // Invalid command
        return 0;
    }
  }
  else if (argv[0] == IVL_DIAG_MODULE_ID) {
    il_voice_get_diagnostics(ilv_diag);
    printstr("il_voice:: ilv_diag.mic_in_peak = "); printintln(ilv_diag.mic_in_peak);
    printstr("il_voice:: ilv_diag.mic_pre_aec_peak = "); printintln(ilv_diag.mic_pre_aec_peak);
    printstr("il_voice:: ilv_diag.mic_out_peak = "); printintln(ilv_diag.mic_out_peak);
    printstr("il_voice:: ilv_diag.spk_in_peak = "); printintln(ilv_diag.spk_in_peak);
    printstr("il_voice:: ilv_diag.spk_out_peak = "); printintln(ilv_diag.spk_out_peak);
    printstr("il_voice:: ilv_diag.aec_delay_ms = "); printintln(ilv_diag.aec_delay_ms);
    printstr("il_voice:: ilv_diag.aec_erle_dB = "); printintln(ilv_diag.aec_erle_dB);
    printstr("\n");
  }

  err = il_voice_update_cfg(ilv_rtcfg);
  if (err) {
    printstr("cntrlAudioProcess:: ERROR il_voice_update_cfg(). Error Code = "); printintln(err);
//      _Exit(1);
  }

  return 1;
}
