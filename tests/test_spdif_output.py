#!/usr/bin/env python
import xmostest
import re
import ntpath

class SPDIFOutputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, spdif_base_chan, sample_rate,
                 duration, os, use_wdm):
            super(SPDIFOutputTester, self).__init__()
            self.product = "sw_usb_audio"
            self.group = "digital_hw_tests"
            self.test = "spdif_output_test"
            self.config = {'app_name':app_name,
                           'app_config':app_config,
                           'spdif_base_chan':spdif_base_chan,
                           'sample_rate':sample_rate,
                           'duration':duration,
                           'os':os,
                           'use_wdm':use_wdm}
            self.register_test(self.product, self.group, self.test, self.config)

    def record_failure(self, failure_reason):
        self.failures.append(failure_reason)
        print "Failure reason: %s" % failure_reason
        self.result = False

    def run(self, dut_programming_output, sig_gen_output, analyzer_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen_output + analyzer_output):
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
                self.record_failure(line)

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'nightly'):
            # Check DUT was flashed correctly
            found = False
            for line in dut_programming_output:
                if re.match('.*Site 0 has finished.*', line):
                    found = True
            if not found:
                self.record_failure("Expected xFLASH success message not seen")

        # Check that the signals detected follow the correct ramps
        expected_chan_step_sizes = [7, -5]
        for i, expected_step in enumerate(expected_chan_step_sizes):
            found = False
            expected_line = ("Channel %d: step = %d" %
                             (self.config['spdif_base_chan']+i, expected_step))
            for line in analyzer_output:
                if line.startswith(expected_line):
                    found = True
            if not found:
                self.record_failure("Expected step of %d not seen on channel %d"
                                    % (expected_step, self.config['spdif_base_chan']+i))

        # Check that there are no discontinuities detected in the signals
        for line in analyzer_output:
            if re.match('.*discontinuity', line):
                self.record_failure("Discontinuity in ramp detected")

        output = {'sig_gen_output':''.join(sig_gen_output),
                  'analyzer_output':''.join(analyzer_output)}
        if not self.result:
            output['failures'] = ''.join(self.failures)
        xmostest.set_test_result(self.product,
                                 self.group,
                                 self.test,
                                 self.config,
                                 self.result,
                                 env={},
                                 output=output)

def do_spdif_output_test(testlevel, board, app_name, app_config, spdif_base_chan,
                         sample_rate, duration, os, use_wdm=False):

    ctester = xmostest.CombinedTester(3, SPDIFOutputTester(app_name, app_config,
                                            spdif_base_chan, sample_rate,
                                            duration, os, use_wdm))
    ctester.set_min_testlevel(testlevel)

    print ("Starting S/PDIF output test at %d on %s:%s under %s" %
           (sample_rate, app_name, app_config, os))
    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                          ctester)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/spdif_out/app_audio_analyzer_mc_spdif_out.xe'

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

    print "Scheduling PC signal generator job"
    run_xsig_path = "../../../../xsig/xsig/bin/"
    xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
    if os.startswith('os_x'):
        run_xsig_path += "run_xsig"
    elif os.startswith('win_'):
        run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
        xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
    if spdif_base_chan is 0:
        xsig_config_file = "stereo_digital_output.json"
    else:
        xsig_config_file = "mc_digital_output.json"
    if use_wdm:
        wdm_arg = "--wdm"
    else:
        wdm_arg = ""
    sig_gen_job = xmostest.run_on_pc(resources['host'],
                                     [run_xsig_path,
                                     "%d" % (sample_rate),
                                     "%d" % ((duration + 10) * 1000), # Ensure signal generator runs for longer than audio analyzer, xsig expects duration in ms
                                     "%s%s" % (xsig_configs_path, xsig_config_file),
                                     wdm_arg],
                                     tester = ctester[1],
                                     timeout = duration + 60, # xsig should stop itself gracefully
                                     initial_delay = 5,
                                     start_after_completed = [dut_job])

    print "Scheduling xCORE analyzer job"
    analysis_job = xmostest.run_on_xcore(resources['analysis_device_1'],
                                          analyser_binary,
                                          tester = ctester[2],
                                          enable_xscope = True,
                                          timeout = duration,
                                          start_after_completed = [dut_job],
                                          start_after_started = [sig_gen_job])

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'2io_spdifout_adatout','spdif_base_chan':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            {'config':'2io_spdifout_spdifin','spdif_base_chan':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            {'config':'2io_spdifout_spdifin_mix8','spdif_base_chan':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            {'config':'2ioxs','spdif_base_chan':8,'testlevels':[
                {'level':'smoke','sample_rates':[44100, 192000]},
                {'level':'nightly','sample_rates':[48000, 88200, 96000, 176400]}]},
            {'config':'2xoxs','spdif_base_chan':8,'testlevels':[
                {'level':'smoke','sample_rates':[44100, 192000]},
                {'level':'nightly','sample_rates':[48000, 88200, 96000, 176400]}]},
            ]
        }
    ]

    host_oss = ['os_x', 'win_vista', 'win_7', 'win_8']
    duration = 30

    if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'nightly'):
        duration = 60 # TODO: set test time for nightlies

    for test in test_configs:
        board = test['board']
        app = test['app']
        for os in host_oss:
            for config in test['app_configs']:
                config_name = config['config']
                spdif_base_chan = config['spdif_base_chan']
                for run_type in config['testlevels']:
                    testlevel = run_type['level']
                    sample_rates = run_type['sample_rates']
                    for sample_rate in sample_rates:
                        do_spdif_output_test(testlevel, board, app, config_name,
                                             spdif_base_chan, sample_rate,
                                             duration, os)

                    # Special case to test WDM on Windows
                    # TODO: confirm WDM values are correct
                    WDM_SAMPLE_RATE = 44100
                    if os.startswith('win_') and WDM_SAMPLE_RATE in sample_rates:
                        do_spdif_output_test(testlevel, board, app, config_name,
                                             spdif_base_chan, WDM_SAMPLE_RATE,
                                             duration, os, use_wdm=True)
