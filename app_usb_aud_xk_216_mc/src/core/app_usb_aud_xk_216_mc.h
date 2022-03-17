
/**
 * @file       app_vf_spk_base.h
 * @brief      Defines relating to device configuration and customisation.
 *             For xCORE-200 Microphone Array board (2vx)
 * @author     Ross Owen, XMOS Limited
 */

#ifndef APP_USB_AUD_XK_216_MC_H_
#define APP_USB_AUD_XK_216_MC_H_

#include "xua_conf.h"

/* Default to board version version 2.0 */
#ifndef XCORE_200_MC_AUDIO_HW_VERSION
#define XCORE_200_MC_AUDIO_HW_VERSION 2
#endif

#ifndef USB_SEL_A
#define USB_SEL_A    (0)
#endif

// Include this header after setting application defaults to then apply any other XUA defaults
#include "xua_conf_full.h"

#endif
