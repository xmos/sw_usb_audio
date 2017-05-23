#!/usr/bin/env python
import xmostest
import re
import ntpath
import time

class VolumeChangeChecker(object):
    def __init__(self):
        self.initial_change = 0

    def initial_decrease(self, failure_reporter, output):
        m = re.match('.*Volume change by -([\d]*)', output)
        try:
            self.initial_change = int(m.groups(0)[0])
        except (AttributeError, ValueError):
            failure_reporter("Cannot interpret initial volume decrease")

    def check_change(self, failure_reporter, output, expected_ratio):
        if  expected_ratio > 0:
            r = '.*Volume change by ([\d]*)'
        else:
            r = '.*Volume change by -([\d]*)'
            expected_ratio = -expected_ratio
        m = re.match(r, output)
        try:
            v = int(m.groups(0)[0])
        except (AttributeError, ValueError):
            failure_reporter("Cannot interpret volume change")
            return
        ratio = float(v)/float(self.initial_change)
        # Test within 15% tolerance
        if (ratio < expected_ratio - 0.15 or ratio > expected_ratio + 0.15):
            failure_reporter("Volume change not as expected")

class VolumeOutputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, num_chans, channel, os):
            super(VolumeOutputTester, self).__init__()
            self.product = "sw_usb_audio"
            self.group = "analogue_hw_tests"
            self.test = "volume_output_test"
            self.config = {'app_name':app_name,
                           'app_config':app_config,
                           'num_chans':num_chans,
                           'channel':channel,
                           'os':os}
            self.register_test(self.product, self.group, self.test, self.config)
            self.EXPECTED_NUM_CHANGES = 6
            self.EXPECTED_INITIAL_VOL = 84

    def record_failure(self, failure_reason):
        # Append a newline if there isn't one already
        if not failure_reason.endswith('\n'):
            failure_reason += '\n'
        self.failures.append(failure_reason)
        print ("Failure reason: %s" % failure_reason), # Print without newline
        self.result = False

    def check_channel(self, analyzer_output, chan):
        chan_output = []

        for line in analyzer_output:
            if line.startswith('Channel %d:' % chan):
                chan_output.append(line)
        if len(chan_output) != self.EXPECTED_NUM_CHANGES:
            self.record_failure("Unexpected number of lines of output seen for channel %d"
                                % chan)
        else:
            volume_checker = VolumeChangeChecker()
            if not chan_output[0].startswith('Channel %d: Set mode to volume check' % chan):
                self.record_failure("Channel %d not set to volume check mode" % chan)
            if not chan_output[1].startswith('Channel %d: Volume change by %d'
                                             % (chan, self.EXPECTED_INITIAL_VOL)):
                self.record_failure("Initial volume level of channel %d was not %ddb"
                                    % (chan, self.EXPECTED_INITIAL_VOL))
            volume_checker.initial_decrease(self.record_failure, chan_output[2])
            volume_checker.check_change(self.record_failure, chan_output[3], 1.0)
            volume_checker.check_change(self.record_failure, chan_output[4], -0.5)
            volume_checker.check_change(self.record_failure, chan_output[5], 0.5)

    def run(self, dut_programming_output, sig_gen_output, analyzer1_output,
            analyzer1_host_xscope_output, analyzer2_output,
            analyzer2_host_xscope_output, vol_ctrl_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen_output +
                     analyzer1_output + analyzer1_host_xscope_output +
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

        # Check that the signals were never lost
        for line in (analyzer1_output + analyzer1_host_xscope_output +
                     analyzer2_output + analyzer2_host_xscope_output):
            if re.match('Channel [0-9]*: Lost signal', line):
                self.record_failure(line)

        # Check each channel transitions through the expected changes of volume
        if self.config['channel'] is 'master':
            for chan in range(self.config['num_chans']):
                self.check_channel((analyzer1_output +
                                    analyzer1_host_xscope_output +
                                    analyzer2_output +
                                    analyzer2_host_xscope_output),
                                   chan)
        else:
            # Check channel transitions through the expected changes of volume
            self.check_channel((analyzer1_output +
                                analyzer1_host_xscope_output +
                                analyzer2_output +
                                analyzer2_host_xscope_output),
                               self.config['channel'])
            # Check all other channels have expected frequency
            for i in range(self.config['num_chans']):
                if i == self.config['channel']:
                    continue # Skip the channel having its volume changed
                found = False
                expected_freq = ((i+1) * 1000) + 500
                expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
                for line in (analyzer1_output + analyzer1_host_xscope_output +
                             analyzer2_output + analyzer2_host_xscope_output):
                    if line.startswith(expected_line):
                        found = True
                if not found:
                    self.record_failure("Expected frequency of %d not seen on channel %d"
                                        % (expected_freq, i))

        output = {'sig_gen_output':''.join(sig_gen_output),
                  'analyzer1_output':''.join(analyzer1_output),
                  'analyzer1_host_xscope_output':''.join(analyzer1_host_xscope_output),
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

class XS2VolumeOutputTester(VolumeOutputTester):

    def __init__(self, *args, **kwargs):
        super(XS2VolumeOutputTester, self).__init__(*args, **kwargs)
        self.EXPECTED_INITIAL_VOL = 87

    def run(self, dut_programming_output, sig_gen_output, analyzer1_output,
            analyzer1_host_xscope_output, vol_ctrl_output):
        super(XS2VolumeOutputTester, self).run(dut_programming_output, sig_gen_output, analyzer1_output,
                                              analyzer1_host_xscope_output, [], [], vol_ctrl_output)

def do_volume_output_test(min_testlevel, board, app_name, app_config, num_chans,
                          sample_rate, channel, host_oss, product_string):

    ctester = {}
    resources = {}
    dut_job = {}
    sig_gen_job = {}
    analysis1_job = {}
    analysis2_job = {}
    volcontrol_job = {}
    duration = 26

    for os in host_oss:

        if board == 'xcore200_mc':
            # Get all testers and resources
            ctester[os] = xmostest.CombinedTester(5, XS2VolumeOutputTester(app_name, app_config,
                                              num_chans, channel, os))
        else:
            ctester[os] = xmostest.CombinedTester(7, VolumeOutputTester(app_name, app_config,
                                  num_chans, channel, os))
        ctester[os].set_min_testlevel(min_testlevel)

        resources[os] = xmostest.request_resource("testrig_%s" % (os),
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
            dut_job[os] = xmostest.flash_xcore(resources[os]['uac2_%s_dut' % (board)],
                                           dut_binary,
                                           tester = ctester[os][0],
                                           start_after_completed = dep_dut_job[:])
            dep_dut_job.append(dut_job[os])
        else:
            dut_job[os] = xmostest.run_on_xcore(resources[os]['uac2_%s_dut' % (board)],
                                            dut_binary,
                                            tester = ctester[os][0],
                                            disable_debug_io = True)

        run_xsig_path = "../../../../xsig/xsig/bin/"
        xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
        if os.startswith('os_x'):
            run_xsig_path += "run_xsig"
        elif os.startswith('win_'):
            run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
            xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
        if num_chans is 2:
            xsig_config_file = "stereo_analogue_output.json"
        else:
            xsig_config_file = "mc_analogue_output.json"

        sig_gen_job[os] = xmostest.run_on_pc(resources[os]['host'],
                                         [run_xsig_path,
                                         "%d" % (sample_rate),
                                         "%d" % ((duration + 10) * 1000), # Ensure signal generator runs for longer than audio analyzer, xsig expects duration in ms
                                         "%s%s" % (xsig_configs_path, xsig_config_file),
                                         "--device", "%s" % product_string],
                                         tester = ctester[os][1],
                                         timeout = duration + 60, # xsig should stop itself gracefully
                                         initial_delay = 8,
                                         start_after_completed = [dut_job[os]])

        (analysis1_debugger_addr, analysis1_debugger_port) = resources[os]['uac2_%s_analysis_device_1' % (board)].get_xscope_port().split(':')
        analysis1_xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                     analysis1_debugger_addr,
                                     analysis1_debugger_port,
                                     "%d" % duration]

        max_channel = 4
        if (board == 'xcore200_mc'):
            max_channel = 8

        if channel is 'master':
            analysis1_xscope_host_cmd.extend("m %d v" % chan for chan in range(max_channel))
        elif channel < max_channel:
            analysis1_xscope_host_cmd.append("m %d v" % channel)
        analysis1_job[os] = xmostest.run_on_xcore(resources[os]['uac2_%s_analysis_device_1' % (board)],
                                              analyser_binary,
                                              tester = ctester[os][2],
                                              enable_xscope = True,
                                              timeout = duration,
                                              start_after_completed = [dut_job[os]],
                                              start_after_started = [sig_gen_job[os]],
                                              xscope_host_cmd = analysis1_xscope_host_cmd,
                                              xscope_host_tester = ctester[os][3],
                                              xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                              xscope_host_initial_delay = 8)
        i_ctester = 4
        dep_analysis_job = []
        dep_analysis_job.append(analysis1_job[os])
        # xCORE-200 MC tester uses only one 'analysis_device'
        if board != 'xcore200_mc':
            (analysis2_debugger_addr, analysis2_debugger_port) = resources[os]['uac2_%s_analysis_device_2' % (board)].get_xscope_port().split(':')
            analysis2_xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                         analysis2_debugger_addr,
                                         analysis2_debugger_port,
                                         "%d" % duration,
                                         "b 4"]
            if channel is 'master':
                analysis2_xscope_host_cmd.extend("m %d v" % chan for chan in range(4, num_chans))
            elif channel >= 4:
                analysis2_xscope_host_cmd.append("m %d v" % channel)
            analysis2_job[os] = xmostest.run_on_xcore(resources[os]['uac2_%s_analysis_device_2' % (board)],
                                                  analyser_binary,
                                                  tester = ctester[os][i_ctester],
                                                  enable_xscope = True,
                                                  timeout = duration,
                                                  initial_delay = 1, # Avoid accessing both xTAGs together
                                                  start_after_completed = [dut_job[os]],
                                                  start_after_started = [sig_gen_job[os],
                                                                         analysis1_job[os]],
                                                  xscope_host_cmd = analysis2_xscope_host_cmd,
                                                  xscope_host_tester = ctester[os][i_ctester + 1],
                                                  xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                                  xscope_host_initial_delay = 8)
            i_ctester += 2
            dep_analysis_job.append(analysis2_job[os])

        if os.startswith('os_x'):
            host_vol_ctrl_path = "../../../../usb_audio_testing/volcontrol/OSX/testvol_out.sh"
        elif os.startswith('win_'):
            host_vol_ctrl_path = "..\\..\\..\\..\\usb_audio_testing\\volcontrol\\win32\\testvol_out.bat"
        if channel is 'master':
            channel_number = 0
        else:
            channel_number = channel + 1

        volcontrol_job[os] = xmostest.run_on_pc(resources[os]['host_secondary'],
                                            [host_vol_ctrl_path,
                                            "%d" % (channel_number),
                                            "%d" % (num_chans+1)],
                                            tester = ctester[os][i_ctester],
                                            timeout = duration + 60, # testvol should stop itself
                                            initial_delay = 14,
                                            # start_after_started = [sig_gen_job[os],
                                            #                        analysis1_job[os],
                                            #                        analysis2_job[os]],
                                            start_after_started = dep_analysis_job,
                                            # start_after_completed = [dut_job[os]]
                                            )
        time.sleep(0.1)

    xmostest.complete_all_jobs()

def runtest():
    # Check if the test is running in an environment with hardware resources
    # available
    args = xmostest.getargs()
    if not args.remote_resourcer:
        # Abort the test
        print 'Remote resourcer not available, aborting test!'
        return

    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','productstringbase':'xCORE L2 USB Audio ','app_configs':[
            {'config':'1ioxx','chan_count':2,
                'max_sample_rate':48000,'testlevel':'nightly'},

            {'config':'1xoxx','chan_count':2,
                'max_sample_rate':48000,'testlevel':'weekend'},

            {'config':'2io_adatin','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},

            {'config':'2io_adatout','chan_count':8,
                'max_sample_rate':96000,'testlevel':'weekend'},

            {'config':'2io_spdifout_adatout','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},

            {'config':'2io_spdifout_spdifin','chan_count':8,
                'max_sample_rate':192000,'testlevel':'weekend'},

            {'config':'2io_spdifout_spdifin_mix8','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'},

            {'config':'2io_tdm8','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},

            {'config':'2iomx','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'},

            {'config':'2ioxs','chan_count':8,
                'max_sample_rate':192000,'testlevel':'smoke'},

            {'config':'2ioxx','chan_count':8,
                'max_sample_rate':192000,'testlevel':'weekend'},

            {'config':'2xoxs','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'}
            ]
        },
        {'board':'xcore200_mc','app':'app_usb_aud_xk_216_mc','productstringbase':'xCORE-200 MC USB Audio ','app_configs':[

            {'config':'2i8o8xxxxx_tdm8','chan_count':8,
                  'max_sample_rate':48000, 'testlevel':'nightly'},
            {'config':'2i10o10xxxxxx','chan_count':8,
                  'max_sample_rate':96000, 'testlevel':'smoke'},
            {'config':'2i10o10msxxxx','chan_count':8,
                  'max_sample_rate':192000, 'testlevel':'nightly'},
            {'config':'2i10o10xsxxxx_mix8','chan_count':8,
                  'max_sample_rate':44100, 'testlevel':'weekend'},
            {'config':'2i10o10xssxxx','chan_count':8,
                  'max_sample_rate':176400, 'testlevel':'weekend'},
            ]
        },
    ]

    args = xmostest.getargs()

    host_oss = ['os_x_11', 'os_x_dev', 'win_7', 'win_8', 'win_10']

    for test in test_configs:
        board = test['board']
        # Run tests only on requested board
        if args.board:
            if args.board != board:
                continue
        app = test['app']
        for config in test['app_configs']:
            config_name = config['config']
            product_string = config['productstringbase'] + config_name[0] + '.0'
            num_chans = config['chan_count']
            max_sample_rate = config['max_sample_rate']
            min_testlevel = config['testlevel']

            # Test the master volume control
            do_volume_output_test(min_testlevel, board, app, config_name,
                                  num_chans, max_sample_rate, 'master',
                                  host_oss, product_string)

            # Test the volume control of each channel
            for chan in range(num_chans):
                do_volume_output_test(min_testlevel, board, app, config_name,
                                      num_chans, max_sample_rate, chan,
                                      host_oss, product_string)
