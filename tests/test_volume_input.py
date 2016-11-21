#!/usr/bin/env python
import xmostest
import re
import ntpath
import time
import os

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

        expected_vol = float(expected_ratio) * float(self.initial_change)

        if (v < expected_vol - 2 or v > expected_vol + 2):
            failure_reporter("Volume change not as expected %d %d" % (expected_vol, self.initial_change))

        #ratio = float(v)/float(self.initial_change)
        # Test within 15% tolerance
        #if (ratio < expected_ratio - 0.15 or ratio > expected_ratio + 0.15):
          #  failure_reporter("Volume change not as expected")

class VolumeInputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, num_chans, channel, os):
            super(VolumeInputTester, self).__init__()
            self.product = "sw_usb_audio"
            self.group = "analogue_hw_tests"
            self.test = "volume_input_test"
            self.config = {'app_name':app_name,
                           'app_config':app_config,
                           'num_chans':num_chans,
                           'channel':channel,
                           'os':os}
            self.register_test(self.product, self.group, self.test, self.config)
            self.EXPECTED_NUM_CHANGES = 5
            self.EXPECTED_INITIAL_VOL = 63

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
            if not chan_output[0].startswith('Channel %d: Volume change by %d dB' % (chan, self.EXPECTED_INITIAL_VOL)):
                self.record_failure("Initial volume level of channel %d was not %ddB" % (chan, self.EXPECTED_INITIAL_VOL))
            volume_checker.initial_decrease(self.record_failure, chan_output[1])
            volume_checker.check_change(self.record_failure, chan_output[2], 1.0)
            volume_checker.check_change(self.record_failure, chan_output[3], -0.5)
            volume_checker.check_change(self.record_failure, chan_output[4], 0.5)

    def run(self, dut_programming_output, sig_gen1_output, sig_gen2_output,
            sig_gen2_host_xscope_output, analyzer_output, vol_ctrl_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen1_output + sig_gen2_output +
                     sig_gen2_host_xscope_output + analyzer_output):
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
        for line in analyzer_output:
            if re.match('Channel [0-9]*: Lost signal', line):
                self.record_failure(line)

        # Check each channel transitions through the expected changes of volume
        if self.config['channel'] is 'master':
            for chan in range(self.config['num_chans']):
                self.check_channel(analyzer_output, chan)
        else:
            # Check channel transitions through the expected changes of volume
            self.check_channel(analyzer_output, self.config['channel'])
            # Check all other channels have expected frequency
            for i in range(self.config['num_chans']):
                if i == self.config['channel']:
                    continue # Skip the channel having its volume changed
                found = False
                expected_freq = (i+1) * 1000
                expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
                for line in analyzer_output:
                    if line.startswith(expected_line):
                        found = True
                if not found:
                    self.record_failure("Expected frequency of %d not seen on channel %d"
                                        % (expected_freq, i))

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

class XS2VolumeInputTester(VolumeInputTester):

    def __init__(self, *args, **kwargs):
        super(XS2VolumeInputTester, self).__init__(*args, **kwargs)
        self.EXPECTED_INITIAL_VOL = 90

    def run(self, dut_programming_output, sig_gen1_output, 
            analyzer_output, vol_ctrl_output):
        super(XS2VolumeInputTester, self).run(dut_programming_output, sig_gen1_output, [],
                                            [], analyzer_output, vol_ctrl_output)

def do_volume_input_test(min_testlevel, board, app_name, app_config, num_chans,
                         sample_rate, channel, host_oss):

    ctester = {}
    resources = {}
    dut_job = {}
    sig_gen1_job = {}
    sig_gen2_job = {}
    analysis_job = {}
    volcontrol_job = {}
    duration = 25

    for host_os in host_oss:

        if board == 'xcore200_mc':  
            ctester[host_os] = xmostest.CombinedTester(4, XS2VolumeInputTester(app_name, app_config,
                                                    num_chans, channel, host_os))
        else:
            ctester[host_os] = xmostest.CombinedTester(6, VolumeInputTester(app_name, app_config,
                                                    num_chans, channel, host_os))
        ctester[host_os].set_min_testlevel(min_testlevel)

        resources[host_os] = xmostest.request_resource("uac2_%s_testrig_%s" % (board, host_os),
                                              ctester[host_os])
        time.sleep(0.01)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'
    if board == 'xcore200_mc':
        analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_xcore200_mc/bin/app_audio_analyzer_xcore200_mc.xe'

    dep_dut_job = []

    for host_os in host_oss:

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
            dut_job[host_os] = xmostest.flash_xcore(resources[host_os]['dut'], dut_binary,
                                           tester = ctester[host_os][0],
                                           start_after_completed = dep_dut_job)
            dep_dut_job.append(dut_job[host_os])
        else:
            dut_job[host_os] = xmostest.run_on_xcore(resources[host_os]['dut'], dut_binary,
                                            tester = ctester[host_os][0],
                                            disable_debug_io = True)

        sig_gen1_job[host_os] = xmostest.run_on_xcore(resources[host_os]['analysis_device_1'],
                                                 analyser_binary,
                                                 tester = ctester[host_os][1],
                                                 enable_xscope = True,
                                                 timeout = duration + 15, # Ensure signal generator runs for longer than audio analyzer
                                                 start_after_completed = [dut_job[host_os]])

        dep_sig_gen_job = []
        dep_sig_gen_job.append(sig_gen1_job[host_os])
        i_ctester = 2
        if (board != 'xcore200_mc'):
            (analysis2_debugger_addr, analysis2_debugger_port) = resources[host_os]['analysis_device_2'].get_xscope_port().split(':')
            sig_gen2_job[host_os] = xmostest.run_on_xcore(resources[host_os]['analysis_device_2'],
                                                 analyser_binary,
                                                 tester = ctester[host_os][i_ctester],
                                                 enable_xscope = True,
                                                 timeout = duration + 15, # Ensure signal generator runs for longer than audio analyzer
                                                 initial_delay = 1, # Avoid accessing both xTAGs together
                                                 start_after_completed = [dut_job[host_os]],
                                                 xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                                 analysis2_debugger_addr,
                                                 analysis2_debugger_port,
                                                 "%d" % (duration + 15), # Ensure host app runs for longer than xCORE app (started with delay)
                                                 "b 4",
                                                 "c 4 5000 0 0 0",
                                                 "c 5 6000 0 0 0"],
                                                 xscope_host_tester = ctester[host_os][i_ctester + 1],
                                                 xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                                 xscope_host_initial_delay = 8)
            i_ctester += 2
            dep_sig_gen_job.append(sig_gen2_job[host_os])

        run_xsig_path = "../../../../xsig/xsig/bin/"
        xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
        if host_os.startswith('os_x'):
            run_xsig_path += "run_xsig"
        elif host_os.startswith('win_'):
            run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
            xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
        if num_chans is 2:
            if channel is 'master':
                xsig_config_file = "stereo_volcheck_in.m.json"
            else:
                xsig_config_file = "stereo_volcheck_in.%d.json" % channel
        else:
            if channel is 'master':
                xsig_config_file = "mc_volcheck_in.m.json"
            else:
                xsig_config_file = "mc_volcheck_in.%d.json" % channel
        if board == 'xcore200_mc':
            cfile = os.path.splitext(xsig_config_file)
            xsig_config_file = cfile[0] + '_8ch' + cfile[1]

        analysis_job[host_os] = xmostest.run_on_pc(resources[host_os]['host'],
                                          [run_xsig_path,
                                          "%d" % (sample_rate),
                                          "%d" % (duration * 1000), # xsig expects duration in ms
                                          "%s%s" % (xsig_configs_path, xsig_config_file)],
                                          tester = ctester[host_os][i_ctester],
                                          timeout = duration + 60, # xsig should stop itself gracefully
                                          initial_delay = 10,
                                          start_after_started = dep_sig_gen_job,
                                          start_after_completed = [dut_job[host_os]])

        if host_os.startswith('os_x'):
            host_vol_ctrl_path = "../../../../usb_audio_testing/volcontrol/OSX/testvol_in.sh"
        elif host_os.startswith('win_'):
            host_vol_ctrl_path = "..\\..\\..\\..\\usb_audio_testing\\volcontrol\\win32\\testvol_in.bat"
        if channel is 'master':
            channel_number = 0
        else:
            channel_number = channel + 1
        i_ctester += 1
        volcontrol_job[host_os] = xmostest.run_on_pc(resources[host_os]['host_secondary'],
                                            [host_vol_ctrl_path,
                                            "%d" % (channel_number),
                                            "%d" % (num_chans+1)],
                                            tester = ctester[host_os][i_ctester],
                                            timeout = duration + 60, # testvol should stop itself
                                            initial_delay = 10,
                                            # start_after_started = [sig_gen1_job[os],
                                            #                        sig_gen2_job[os],
                                            #                        analysis_job[os]],
                                            start_after_started = [analysis_job[host_os]]
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
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'1ioxx','chan_count':2,
                'max_sample_rate':48000,'testlevel':'nightly'},

            {'config':'2io_adatin','chan_count':6,
                'max_sample_rate':96000,'testlevel':'weekend'},

            {'config':'2io_adatout','chan_count':6,
                'max_sample_rate':96000,'testlevel':'nightly'},

            {'config':'2io_spdifout_adatout','chan_count':6,
                'max_sample_rate':96000,'testlevel':'weekend'},

            {'config':'2io_spdifout_spdifin','chan_count':6,
                'max_sample_rate':192000,'testlevel':'nightly'},

            {'config':'2io_spdifout_spdifin_mix8','chan_count':6,
                'max_sample_rate':192000,'testlevel':'weekend'},

            {'config':'2io_tdm8','chan_count':6,
                'max_sample_rate':96000,'testlevel':'nightly'},

            {'config':'2iomx','chan_count':6,
                'max_sample_rate':192000,'testlevel':'smoke'},

            {'config':'2ioxs','chan_count':6,
                'max_sample_rate':192000,'testlevel':'nightly'},

            {'config':'2ioxx','chan_count':6,
                'max_sample_rate':192000,'testlevel':'weekend'}
            ]
        },
        {'board':'xcore200_mc','app':'app_usb_aud_xk_216_mc','app_configs':[

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
            num_chans = config['chan_count']
            max_sample_rate = config['max_sample_rate']
            min_testlevel = config['testlevel']

            # Test the master volume control
            do_volume_input_test(min_testlevel, board, app, config_name,
                                 num_chans, max_sample_rate, 'master', host_oss)

            # Test the volume control of each channel
            for chan in range(num_chans):
                do_volume_input_test(min_testlevel, board, app, config_name,
                                     num_chans, max_sample_rate, chan, host_oss)
