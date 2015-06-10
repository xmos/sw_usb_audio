#!/usr/bin/env python
import xmostest
import re
import ntpath

class VolumeChangeChecker(object):
    def __init__(self):
        self.initial_change = 0

    def initial_decrease(self, failure_reporter, output):
        m = re.match('.*Volume change by -([\d]*)', output)
        try:
            self.initial_change = int(m.groups(0)[0])
        except AttributeError, ValueError:
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
        except AttributeError, ValueError:
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

    def record_failure(self, failure_reason):
        self.failures.append(failure_reason)
        print "Failure reason: %s" % failure_reason
        self.result = False

    def check_channel(self, analyzer_output, chan):
        EXPECTED_NUM_CHANGES = 6
        EXPECTED_INITIAL_VOL = 84
        chan_output = []

        for line in analyzer_output:
            if line.startswith('Channel %d:' % chan):
                chan_output.append(line)
        if len(chan_output) != EXPECTED_NUM_CHANGES:
            self.record_failure("Unexpected number of lines of output seen for channel %d"
                                % chan)
        else:
            volume_checker = VolumeChangeChecker()
            if not chan_output[0].startswith('Channel %d: Set mode to volume check' % chan):
                self.record_failure("Channel %d not set to volume check mode" % chan)
            if not chan_output[1].startswith('Channel %d: Volume change by %d'
                                             % (chan, EXPECTED_INITIAL_VOL)):
                self.record_failure("Initial volume level of channel %d was not %ddb"
                                    % (chan, EXPECTED_INITIAL_VOL))
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

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'nightly'):
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

def do_volume_output_test(testlevel, board, app_name, app_config, num_chans,
                          sample_rate, channel, os):

    ctester = xmostest.CombinedTester(7, VolumeOutputTester(app_name, app_config,
                                      num_chans, channel, os))
    ctester.set_min_testlevel(testlevel)

    duration = 20

    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                          ctester)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'

    if xmostest.testlevel_is_at_least(testlevel, 'nightly'):
        dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                       tester = ctester[0])
    else:
        dut_job = xmostest.run_on_xcore(resources['dut'], dut_binary,
                                        tester = ctester[0],
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
    sig_gen_job = xmostest.run_on_pc(resources['host'],
                                     [run_xsig_path,
                                     "%d" % (sample_rate),
                                     "%d" % ((duration + 10) * 1000), # Ensure signal generator runs for longer than audio analyzer, xsig expects duration in ms
                                     "%s%s" % (xsig_configs_path, xsig_config_file)],
                                     tester = ctester[1],
                                     timeout = duration + 60, # xsig should stop itself gracefully
                                     initial_delay = 5,
                                     start_after_completed = [dut_job])

    (analysis1_debugger_addr, analysis1_debugger_port) = resources['analysis_device_1'].get_xscope_port().split(':')
    analysis1_xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                 analysis1_debugger_addr,
                                 analysis1_debugger_port,
                                 "%d" % duration]
    if channel is 'master':
        analysis1_xscope_host_cmd.extend("m %d v" % chan for chan in range(4))
    elif channel < 4:
        analysis1_xscope_host_cmd.append("m %d v" % channel)
    analysis1_job = xmostest.run_on_xcore(resources['analysis_device_1'],
                                          analyser_binary,
                                          tester = ctester[2],
                                          enable_xscope = True,
                                          timeout = duration,
                                          start_after_completed = [dut_job],
                                          start_after_started = [sig_gen_job],
                                          xscope_host_cmd = analysis1_xscope_host_cmd,
                                          xscope_host_tester = ctester[3],
                                          xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                          xscope_host_initial_delay = 5)

    (analysis2_debugger_addr, analysis2_debugger_port) = resources['analysis_device_2'].get_xscope_port().split(':')
    analysis2_xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                 analysis2_debugger_addr,
                                 analysis2_debugger_port,
                                 "%d" % duration,
                                 "b 4"]
    if channel is 'master':
        analysis2_xscope_host_cmd.extend("m %d v" % chan for chan in range(4, num_chans))
    elif channel >= 4:
        analysis2_xscope_host_cmd.append("m %d v" % channel)
    analysis2_job = xmostest.run_on_xcore(resources['analysis_device_2'],
                                          analyser_binary,
                                          tester = ctester[4],
                                          enable_xscope = True,
                                          timeout = duration,
                                          initial_delay = 1, # Avoid accessing both xTAGs together
                                          start_after_completed = [dut_job],
                                          start_after_started = [sig_gen_job,
                                                                 analysis1_job],
                                          xscope_host_cmd = analysis2_xscope_host_cmd,
                                          xscope_host_tester = ctester[5],
                                          xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                          xscope_host_initial_delay = 5)

    if os.startswith('os_x'):
        host_vol_ctrl_path = "../../../../usb_audio_testing/volcontrol/OSX/testvol_out.sh"
    elif os.startswith('win_'):
        host_vol_ctrl_path = "..\\..\\..\\..\\usb_audio_testing\\volcontrol\\win32\\testvol_out.bat"
    if channel is 'master':
        channel_number = 0
    else:
        channel_number = channel + 1
    volcontrol_job = xmostest.run_on_pc(resources['host_secondary'],
                                        [host_vol_ctrl_path,
                                        "%d" % (channel_number),
                                        "%d" % (num_chans+1)],
                                        tester = ctester[6],
                                        timeout = duration + 60, # testvol should stop itself
                                        initial_delay = 10,
                                        # start_after_started = [sig_gen_job,
                                        #                        analysis1_job,
                                        #                        analysis2_job],
                                        start_after_started = [analysis1_job,
                                                               analysis2_job]
                                        # start_after_completed = [dut_job]
                                        )

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'1ioxx','chan_count':2,
                'max_sample_rate':48000,'testlevel':'nightly'},
            
            {'config':'1xoxx','chan_count':2,
                'max_sample_rate':48000,'testlevel':'nightly'},
            
            {'config':'2io_adatin','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},
            
            {'config':'2io_adatout','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},
            
            {'config':'2io_spdifout_adatout','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},
            
            {'config':'2io_spdifout_spdifin','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'},
            
            {'config':'2io_spdifout_spdifin_mix8','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'},
            
            {'config':'2io_tdm8','chan_count':8,
                'max_sample_rate':96000,'testlevel':'nightly'},
            
            {'config':'2iomx','chan_count':8,
                'max_sample_rate':192000,'testlevel':'nightly'},
            
            {'config':'2ioxs','chan_count':8,
                'max_sample_rate':192000,'testlevel':'smoke'},
            
            {'config':'2ioxx','chan_count':8,
                'max_sample_rate':192000,'testlevel':'smoke'},
            
            {'config':'2xoxs','chan_count':8,
                'max_sample_rate':192000,'testlevel':'smoke'}
            ]
        }
    ]

    host_oss = ['os_x', 'win_vista', 'win_7', 'win_8']

    for test in test_configs:
        board = test['board']
        app = test['app']
        for os in host_oss:
            for config in test['app_configs']:
                config_name = config['config']
                num_chans = config['chan_count']
                max_sample_rate = config['max_sample_rate']
                testlevel = config['testlevel']

                # Test the master volume control
                do_volume_output_test(testlevel, board, app, config_name,
                                      num_chans, max_sample_rate, 'master',
                                      os)

                # Test the volume control of each channel
                for chan in range(num_chans):
                    do_volume_output_test(testlevel, board, app, config_name,
                                          num_chans, max_sample_rate, chan,
                                          os)
