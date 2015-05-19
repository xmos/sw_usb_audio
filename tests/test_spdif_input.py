#!/usr/bin/env python
import xmostest
import re
import ntpath

class SPDIFInputTester(xmostest.Tester):

    def __init__(self):
            super(SPDIFInputTester, self).__init__()

    def run(self, dut_programming_output, sig_gen_output, analyzer_output,
            os, app_name, app_config, freq, duration, spdif_base_chan, use_wdm):
        result = True

        # Check for any errors
        for line in (dut_programming_output + sig_gen_output + analyzer_output):
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
                print "Failure reason: Error message seen"
                result = False

        if xmostest.get_testlevel() != 'smoke':
            # Check DUT was flashed correctly
            found = False
            for line in dut_programming_output:
                if re.match('.*Site 0 has finished.*', line):
                    found = True
            if not found:
                print "Failure reason: Expected xFLASH success message not seen"
                result = False

        # Check that the signals detected follow the correct ramps
        expected_chan_step_sizes = [7, -5]
        for i, expected_step in enumerate(expected_chan_step_sizes):
            found = False
            expected_line = ("Channel %d: step = %d" %
                             (spdif_base_chan+i, expected_step))
            for line in analyzer_output:
                if line.startswith(expected_line):
                    found = True
            if not found:
                print ("Failure reason: Expected step of %d not seen on channel %d"
                       % (expected_step, spdif_base_chan+i))
                result = False

        # Check that there are no discontinuities detected in the signals
        for line in analyzer_output:
            if re.match('.*discontinuity', line):
                print "Failure reason: Discontinuity in ramp detected"
                result = False

        xmostest.set_test_result("sw_usb_audio",
                                 "digital_hw_tests",
                                 "spdif_input_test",
                                 config={'app_name':app_name,
                                        'spdif_base_chan':spdif_base_chan,
                                        'duration':duration,
                                        'os':os,
                                        'use_wdm':use_wdm,
                                        'app_config':app_config,
                                        'freq':freq},
                                 result=result,
                                 env={},
                                 output={'sig_gen_output':''.join(sig_gen_output),
                                         'analyzer_output':''.join(analyzer_output)})

def do_spdif_input_test(board, os, app_name, app_config, freq, duration,
                        spdif_base_chan, use_wdm=False):
    print ("Starting S/PDIF input test at %d on %s:%s under %s" %
           (freq, app_name, app_config, os))
    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os))

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/spdif_in/app_audio_analyzer_mc_spdif_in.xe'

    ctester = xmostest.CombinedTester(3, SPDIFInputTester(),
                                      os, app_name, app_config, freq, duration,
                                      spdif_base_chan, use_wdm)

    if xmostest.get_testlevel() != 'smoke':
        print "Scheduling DUT flashing job"
        dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                         tester = ctester[0],
                                         initial_delay = None)
    else:
        print "Scheduling DUT xrun job"
        dut_job = xmostest.run_on_xcore(resources['dut'], dut_binary,
                                        tester = ctester[0],
                                        disable_debug_io = True)

    print "Scheduling xCORE signal generator job"
    sig_gen_job = xmostest.run_on_xcore(resources['analysis_device_1'],
                                         analyser_binary,
                                         tester = ctester[1],
                                         enable_xscope = True,
                                         timeout = duration + 10, # Ensure signal generator runs for longer than audio analyzer
                                         start_after_completed = [dut_job])

    print "Scheduling PC analyzer job"
    run_xsig_path = "../../../../xsig/xsig/bin/"
    xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
    if os.startswith('os_x'):
        run_xsig_path += "run_xsig"
    elif os.startswith('win_'):
        run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
        xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
    if spdif_base_chan is 0:
        xsig_config_file = "stereo_digital_input.json"
    else:
        xsig_config_file = "mc_digital_input.json"
    if use_wdm:
        wdm_arg = "--wdm"
    else:
        wdm_arg = ""
    analysis_job = xmostest.run_on_pc(resources['host'],
                                      [run_xsig_path,
                                      "%d" % (freq),
                                      "%d" % (duration * 1000), # xsig expects duration in ms
                                      "%s%s" % (xsig_configs_path, xsig_config_file),
                                      wdm_arg],
                                      tester = ctester[2],
                                      timeout = duration + 60, # xsig should stop itself gracefully
                                      initial_delay = 5,
                                      start_after_started = [sig_gen_job],
                                      start_after_completed = [dut_job])

def runtest():
    # key = friendly board name : values = 'app name', [(app config, S/PDIF channel offset, [sample freqs...], test level)...]
    APP_NAME_OFFSET = 0
    CONFIG_LIST_OFFSET = 1
    CONFIG_NAME_OFFSET = 0
    CONFIG_SPDIF_BASE_CHAN_OFFSET = 1
    CONFIG_SAMPLE_FREQS_OFFSET = 2
    CONFIG_TEST_LEVEL_OFFSET = 3
    tests = {
             'l2' : ('app_usb_aud_l2', [('2io_spdifout_spdifin', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'smoke'),
                                        ('2io_spdifout_spdifin_mix8', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'nightly')])
            }

    if xmostest.get_testlevel() != 'smoke':
        audio_boards = ['l2']
        host_oss = ['os_x', 'win_vista', 'win_7', 'win_8']
        test_freqs = [44100, 48000, 88200, 96000, 176400, 192000]
        duration = 60 # TODO: set test time for nightlies
    else:
        # Smoke test only
        audio_boards = ['l2']
        host_oss = ['os_x']
        test_freqs = [44100, 192000]
        duration = 30

    for board in audio_boards:
        app = tests[board][APP_NAME_OFFSET]
        for os in host_oss:
            for config in tests[board][CONFIG_LIST_OFFSET]:
                required_testlevel = config[CONFIG_TEST_LEVEL_OFFSET]
                if xmostest.testlevel_is_at_least(xmostest.get_testlevel(),
                                                  required_testlevel):
                    config_name = config[CONFIG_NAME_OFFSET]
                    spdif_base_chan = config[CONFIG_SPDIF_BASE_CHAN_OFFSET]
                    sample_freqs = config[CONFIG_SAMPLE_FREQS_OFFSET]

                    for freq in sample_freqs:
                        if freq in test_freqs:
                            do_spdif_input_test(board, os, app, config_name,
                                                freq, duration, spdif_base_chan)

                    # Special case to test WDM on Windows
                    # TODO: confirm WDM values are correct
                    WDM_SUPPORTED_FREQ = 44100
                    if os.startswith('win_') and WDM_SUPPORTED_FREQ in sample_freqs:
                        do_spdif_input_test(board, os, app, config_name,
                                            WDM_SUPPORTED_FREQ, duration,
                                            spdif_base_chan, use_wdm=True)
