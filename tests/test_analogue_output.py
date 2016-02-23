#!/usr/bin/env python
import xmostest
import re
import ntpath
import time

class AnalogueOutputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, num_chans, sample_rate, duration,
                 os, use_wdm):
        super(AnalogueOutputTester, self).__init__()
        self.product = "sw_usb_audio"
        self.group = "analogue_hw_tests"
        self.test = "analogue_output_test"
        self.config = {'app_name':app_name,
                       'app_config':app_config,
                       'num_chans':num_chans,
                       'sample_rate':sample_rate,
                       'duration':duration,
                       'os':os,
                       'use_wdm':use_wdm}
        self.register_test(self.product, self.group, self.test, self.config)

    def record_failure(self, failure_reason):
        # Append a newline if there isn't one already
        if not failure_reason.endswith('\n'):
            failure_reason += '\n'
        self.failures.append(failure_reason)
        print ("Failure reason: %s" % failure_reason), # Print without newline
        self.result = False

    def run(self, dut_programming_output, sig_gen_output, analyzer1_output,
            analyzer2_output, analyzer2_host_xscope_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen_output + analyzer1_output +
                     analyzer2_output + analyzer2_host_xscope_output):
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
                self.record_failure(line)

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
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
            expected_freq = ((i+1) * 1000) + 500
            expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
            for line in (analyzer1_output + analyzer2_output +
                         analyzer2_host_xscope_output):
                if line.startswith(expected_line):
                    found = True
            if not found:
                self.record_failure("Expected frequency of %d not seen on channel %d"
                                    % (expected_freq, i))

        for line in (analyzer1_output + analyzer2_output +
                     analyzer2_host_xscope_output):
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

        output = {'sig_gen_output':''.join(sig_gen_output),
                  'analyzer1_output':''.join(analyzer1_output),
                  'analyzer2_output':''.join(analyzer2_output),
                  'analyzer2_host_xscope_output':''.join(analyzer2_host_xscope_output)}
        if not self.result:
            output['failures'] = ''.join(self.failures)
        xmostest.set_test_result(self.product,
                                 self.group,
                                 self.test,
                                 self.config,
                                 self.result,
                                 env={},
                                 output=output)

class XS2AnalogueOutputTester(AnalogueOutputTester):

    # xCORE-200 MC tests uses only one "analyzer" device and doesn't
    # require xscope controller too.
    def run(self, dut_programming_output, sig_gen_output, analyzer1_output):
        return super(XS2AnalogueOutputTester, self).run(dut_programming_output, sig_gen_output,
                                                        analyzer1_output, [], [])

def do_analogue_output_test(min_testlevel, board, app_name, app_config,
                            num_chans, sample_rate, duration, host_oss, use_wdm=False):

    ctester = {}
    resources = {}
    dut_job = {}
    sig_gen_job = {}
    analysis1_job = {}
    analysis2_job = {}
    tester_count = 5
    if board == 'xcore200_mc':
        # Just three tester instances
        tester_count = 3

    for os in host_oss:

        if board == 'xcore200_mc':
            ctester[os] = xmostest.CombinedTester(tester_count, XS2AnalogueOutputTester(app_name,
                                                  app_config, num_chans, sample_rate,
                                                  duration, os, use_wdm))
        else:
            ctester[os] = xmostest.CombinedTester(tester_count, AnalogueOutputTester(app_name,
                                                  app_config, num_chans, sample_rate,
                                                  duration, os, use_wdm))
        ctester[os].set_min_testlevel(min_testlevel)

        resources[os] = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                          ctester[os])
        time.sleep(0.01)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'
    if board == 'xcore200_mc':
        analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_xcore200_mc/bin/app_audio_analyzer_xcore200_mc.xe'
    
    dep_dut_job = []

    for os in host_oss:

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
            dut_job[os] = xmostest.flash_xcore(resources[os]['dut'], dut_binary,
                                              tester = ctester[os][0],
                                              start_after_completed = dep_dut_job) # Flash the DUT separately
            dep_dut_job.append(dut_job[os])
            # FIXME: access all XTAG in parallel for flashing the DUT
        else:
            dut_job[os] = xmostest.run_on_xcore(resources[os]['dut'], dut_binary,
                                            tester = ctester[os][0],
                                            disable_debug_io = True)

        run_xsig_path = "../../../../xsig/xsig/bin/"
        xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
        if os.startswith('os_x'):
            run_xsig_path += "run_xsig"
        elif os.startswith('win_'):
            run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
            xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
        elif os.startswith('lin'):
            run_xsig_path += 'xsig'

        # TODO: xsig should distinguish between L2 and xCORE-200 MC boards
        if num_chans is 2:
            xsig_config_file = "stereo_analogue_output.json"
        else:
            xsig_config_file = "mc_analogue_output.json"
        if use_wdm:
            wdm_arg = "--wdm"
        else:
            wdm_arg = ""

        sig_gen_job[os] = xmostest.run_on_pc(resources[os]['host'],
                                         [run_xsig_path,
                                         "%d" % (sample_rate),
                                         "%d" % ((duration + 10) * 1000), # Ensure signal generator runs for longer than audio analyzer, xsig expects duration in ms
                                         "%s%s" % (xsig_configs_path, xsig_config_file),
                                         wdm_arg],
                                         tester = ctester[os][1],
                                         timeout = duration + 60, # xsig should stop itself gracefully
                                         initial_delay = 8,
                                         start_after_completed = [dut_job[os]])

        analysis1_job[os] = xmostest.run_on_xcore(resources[os]['analysis_device_1'],
                                              analyser_binary,
                                              tester = ctester[os][2],
                                              enable_xscope = True,
                                              timeout = duration,
                                              start_after_completed = [dut_job[os]],
                                              start_after_started = [sig_gen_job[os]])

        if board != 'xcore200_mc':
            (analysis2_debugger_addr, analysis2_debugger_port) = resources[os]['analysis_device_2'].get_xscope_port().split(':')
            analysis2_job[os] = xmostest.run_on_xcore(resources[os]['analysis_device_2'],
                                                  analyser_binary,
                                                  tester = ctester[os][3],
                                                  enable_xscope = True,
                                                  timeout = duration,
                                                  initial_delay = 1, # Avoid accessing both xTAGs together
                                                  start_after_completed = [dut_job[os]],
                                                  start_after_started = [sig_gen_job[os]],
                                                  xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                                  analysis2_debugger_addr,
                                                  analysis2_debugger_port,
                                                  "%d" % duration,
                                                  "b 4"],
                                                  xscope_host_tester = ctester[os][4],
                                                  xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                                  xscope_host_initial_delay = 7)
        time.sleep(0.1)
    xmostest.complete_all_jobs()

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'1ioxx','chan_count':2,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100]}]},

            {'config':'1xoxx','chan_count':2,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100]}]},

            {'config':'2io_adatin','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},

            {'config':'2io_adatout','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[96000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200]}]},

            {'config':'2io_spdifout_adatout','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[96000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200]}]},

            {'config':'2io_spdifout_spdifin','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},

            {'config':'2io_spdifout_spdifin_mix8','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},

            {'config':'2io_tdm8','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[96000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200]}]},

            {'config':'2iomx','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},

            {'config':'2ioxs','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},

            {'config':'2ioxx','chan_count':8,'testlevels':[
                {'level':'smoke','sample_rates':[192000]},
                {'level':'nightly','sample_rates':[176400]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000]}]},

            {'config':'2xoxs','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]}
            ]
        },
        # xCORE-200 MC board test configs
        {'board':'xcore200_mc','app':'app_usb_aud_xk_216_mc','app_configs':[
            {'config':'2i8o8xxxxx_tdm8','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100]},
                {'level':'weekend','sample_rates':[48000, 88200, 96000]},
                {'level':'smoke','sample_rates':[96000]}]},
            
            {'config':'2i8o8xxxxx_tdm8_slave','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100]},
                {'level':'weekend','sample_rates':[48000, 88200, 96000]},
                {'level':'smoke','sample_rates':[96000]}]},

            {'config':'2i10o10xxxxxx','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100, 88200, 96000, 176400]},
                {'level':'smoke','sample_rates':[192000]}]},

            {'config':'2i10o10msxxxx','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100, 88200, 96000, 176400]},
                {'level':'smoke','sample_rates':[192000]}]},

            {'config':'2i10o10xsxxxx_mix8','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100, 88200, 96000, 176400]},
                {'level':'smoke','sample_rates':[192000]}]},

            {'config':'2i10o10xssxxx','chan_count':8,'testlevels':[
                {'level':'nightly','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[44100, 88200, 96000, 176400]},
                {'level':'smoke','sample_rates':[192000]}]},
            ]
        }
    ]

    args = xmostest.getargs()
    
    host_oss = ['os_x_11', 'os_x_dev', 'win_7', 'win_8', 'win_10']
    duration = 30

    if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'nightly'):
        duration = 30 # TODO: set test time for nightlies

    for test in test_configs:
        board = test['board']
        # Run tests only on requested board
        if args.board:
            if args.board != board:
                continue
        app = test['app']
        for config in test['app_configs']:
            config_name = config['config']
            num_chans = config['chan_count']
            for run_type in config['testlevels']:
                min_testlevel = run_type['level']
                sample_rates = run_type['sample_rates']
                for sample_rate in sample_rates:
                    do_analogue_output_test(min_testlevel, board, app,
                                            config_name, num_chans,
                                            sample_rate, duration, host_oss)
                win_oss = []
                for os in host_oss:
                    # Special case to test WDM on Windows
                    # TODO: confirm WDM values are correct
                    WDM_SAMPLE_RATE = 44100
                    WDM_MAX_NUM_CHANS = 2
                    if os.startswith('win_') and (WDM_SAMPLE_RATE in sample_rates):
                        win_oss.append(os)

                do_analogue_output_test(min_testlevel, board, app,
                                        config_name, WDM_MAX_NUM_CHANS,
                                        WDM_SAMPLE_RATE, duration, win_oss,
                                        use_wdm=True)
