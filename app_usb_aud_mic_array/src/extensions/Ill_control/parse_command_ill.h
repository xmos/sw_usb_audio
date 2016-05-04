#define IVL_MAX_NUM_MODULE_ARGS 16

// Old Illusonic control protocol is ASCII based so do conversion first
void asciify(uint8_t buffer[], int num_bytes_read, int &argc, int argv[IVL_MAX_NUM_MODULE_ARGS]);

//Process the arguments decoded from ASCII and modify illusonic parameters accordingly
int cntrlAudioProcess(il_voice_rtcfg_t &ilv_rtcfg, il_voice_cfg_t &ilv_cfg,  il_voice_diagnostics_t &ilv_diag, int argc, int argv[IVL_MAX_NUM_MODULE_ARGS]);
