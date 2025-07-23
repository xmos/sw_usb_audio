// Copyright 2025 XMOS LIMITED.
// This Software is subject to the terms of the XMOS Public Licence: Version 1.

on tile[1]: {
                par
                {
                    unsafe
                    {
                        uc_audiohw = (chanend) c_audiohw;
                    }
                }
            }
on tile[0]: {
                par
                {
                    AudioHwRemote(c_audiohw);
                }
            }


