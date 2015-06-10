#!/usr/bin/env python
import xmostest
import re
import ntpath

class AnalogueInputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, num_chans, sample_rate, duration,
                 os, use_wdm):
            super(AnalogueInputTester, self).__init__()
            self.product = "sw_usb_audio"
            self.group = "analogue_hw_tests"
            self.test = "analogue_input_test"
            self.config = {'app_name':app_name,
                           'app_config':app_config,
                           'num_chans':num_chans,
                           'sample_rate':sample_rate,
                           'duration':duration,
                           'os':os,
                           'use_wdm':use_wdm}
            self.register_test(self.product, self.group, self.test, self.config)

    def record_failure(self, failure_reason):
        self.failures.append(failure_reason)
        print "Failure reason: %s" % failure_reason
        self.result = False

    def run(self, dut_programming_output, sig_gen1_output,
            sig_gen2_output, sig_gen2_host_xscope_output, analyzer_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen1_output + sig_gen2_output +
                     sig_gen2_host_xscope_output + analyzer_output):
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

        # Check that the signals detected are of the correct frequencies
        for i in range(self.config['num_chans']):
            found = False
            expected_freq = (i+1) * 1000
            expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
            for line in analyzer_output:
                if line.startswith(expected_line):
                    found = True
            if not found:
                self.record_failure("Expected frequency of %d not seen on channel %d"
                                    % (expected_freq, i))

        for line in analyzer_output:
            # Check that the signals were never lost
            if re.match('Channel [0-9]*: Lost signal', line):
                self.record_failure(line)
            # Check that unexpected signals are not detected
            if re.match('Channel [0-9]*: Signal detected .*', line):
                chan_num = int(re.findall('\d', line)[0])
                if chan_num not in range(0, self.config['num_chans']):
                    self.record_failure("Unexpected signal detected on channel %d"
                                        % chan_num)
            if re.match('Channel [0-9]*: Frequency [0-9]* .*', line):
                chan_num = int(re.findall('\d', line)[0])
                if chan_num not in range(0, self.config['num_chans']):
                    self.record_failure("Unexpected frequency reported on channel %d"
                                        % chan_num)

        output = {'sig_gen1_output':''.join(sig_gen1_output),
                  'sig_gen2_output':''.join(sig_gen2_output),
                  'sig_gen2_host_xscope_output':''.join(sig_gen2_host_xscope_output),
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

def do_analogue_input_test(testlevel, board, app_name, app_config, num_chans,
                           sample_rate, duration, os, use_wdm=False):

    ctester = xmostest.CombinedTester(5, AnalogueInputTester(app_name,
                                            app_config, num_chans, sample_rate,
                                            duration, os, use_wdm))
    ctester.set_min_testlevel(testlevel)

    print ("Starting analogue input test at %d on %s:%s under %s" %
           (sample_rate, app_name, app_config, os))
    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                          ctester)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'

    if xmostest.testlevel_is_at_least(testlevel, 'nightly'):
        print "Scheduling DUT flashing job"
        dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                       tester = ctester[0])
    else:
        print "Scheduling DUT xrun job"
        dut_job = xmostest.run_on_xcore(resources['dut'], dut_binary,
                                        tester = ctester[0],
                                        disable_debug_io = True)

    print "Scheduling xCORE signal generator jobs"
    sig_gen1_job = xmostest.run_on_xcore(resources['analysis_device_1'],
                                         analyser_binary,
                                         tester = ctester[1],
                                         enable_xscope = True,
                                         timeout = duration + 10, # Ensure signal generator runs for longer than audio analyzer
                                         start_after_completed = [dut_job])

    (analysis2_debugger_addr, analysis2_debugger_port) = resources['analysis_device_2'].get_xscope_port().split(':')
    sig_gen2_job = xmostest.run_on_xcore(resources['analysis_device_2'],
                                         analyser_binary,
                                         tester = ctester[2],
                                         enable_xscope = True,
                                         timeout = duration + 10, # Ensure signal generator runs for longer than audio analyzer
                                         initial_delay = 1, # Avoid accessing both xTAGs together
                                         start_after_completed = [dut_job],
                                         xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                         analysis2_debugger_addr,
                                         analysis2_debugger_port,
                                         "%d" % (duration + 10), # Ensure host app runs for longer than xCORE app (started with delay)
                                         "b 4",
                                         "c 4 5000 0 0 0",
                                         "c 5 6000 0 0 0"],
                                         xscope_host_tester = ctester[3],
                                         xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                         xscope_host_initial_delay = 5)

    print "Scheduling PC analyzer job"
    run_xsig_path = "../../../../xsig/xsig/bin/"
    xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
    if os.startswith('os_x'):
        run_xsig_path += "run_xsig"
    elif os.startswith('win_'):
        run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
        xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
    if num_chans is 2:
        xsig_config_file = "stereo_analogue_input.json"
    else:
        xsig_config_file = "mc_analogue_input.json"
    if use_wdm:
        wdm_arg = "--wdm"
    else:
        wdm_arg = ""
    analysis_job = xmostest.run_on_pc(resources['host'],
                                      [run_xsig_path,
                                      "%d" % (sample_rate),
                                      "%d" % (duration * 1000), # xsig expects duration in ms
                                      "%s%s" % (xsig_configs_path, xsig_config_file),
                                      wdm_arg],
                                      tester = ctester[4],
                                      timeout = duration + 60, # xsig should stop itself gracefully
                                      initial_delay = 5,
                                      start_after_started = [sig_gen1_job, sig_gen2_job],
                                      start_after_completed = [dut_job])

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'1ioxx','chan_count':2,'testlevels':[
                {'level':'smoke','sample_rates':[44100]},
                {'level':'nightly','sample_rates':[48000]}]},
            
            {'config':'2io_adatin','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            
            {'config':'2io_adatout','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000]}]},
            
            {'config':'2io_spdifout_adatout','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000]}]},
            
            {'config':'2io_spdifout_spdifin','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            
            {'config':'2io_spdifout_spdifin_mix8','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000, 176400, 192000]}]},
            
            {'config':'2io_tdm8','chan_count':6,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 88200, 96000]}]},
            
            {'config':'2iomx','chan_count':6,'testlevels':[
                {'level':'smoke','sample_rates':[44100, 192000]},
                {'level':'nightly','sample_rates':[48000, 88200, 96000, 176400]}]},
            
            {'config':'2ioxs','chan_count':6,'testlevels':[
                {'level':'smoke','sample_rates':[44100, 192000]},
                {'level':'nightly','sample_rates':[48000, 88200, 96000, 176400]}]},
            
            {'config':'2ioxx','chan_count':6,'testlevels':[
                {'level':'smoke','sample_rates':[44100, 192000]},
                {'level':'nightly','sample_rates':[48000, 88200, 96000, 176400]}]}
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
                num_chans = config['chan_count']
                for run_type in config['testlevels']:
                    testlevel = run_type['level']
                    sample_rates = run_type['sample_rates']
                    for sample_rate in sample_rates:
                        do_analogue_input_test(testlevel, board, app,
                                               config_name, num_chans,
                                               sample_rate, duration, os)

                    # Special case to test WDM on Windows
                    # TODO: confirm WDM values are correct
                    WDM_SAMPLE_RATE = 44100
                    WDM_MAX_NUM_CHANS = 2
                    if os.startswith('win_') and (WDM_SAMPLE_RATE in sample_rates):
                        do_analogue_input_test(testlevel, board, app,
                                               config_name, WDM_MAX_NUM_CHANS,
                                               WDM_SAMPLE_RATE, duration,
                                               os, use_wdm=True)
