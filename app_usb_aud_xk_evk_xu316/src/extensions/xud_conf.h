// Copyright 2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.
#ifndef _XUD_CONF_H_
#define _XUD_CONF_H_

#ifdef LOW_POWER_ENABLE
// Delete the call to set_thread_fast_mode_on in XUD by defining the built-in as ""
#define __builtin_set_thread_fast()
#endif

#endif
