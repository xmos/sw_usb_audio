#!/usr/bin/env python
import xmostest
import re
import ntpath

class VolumeChangeChecker(object):
    def __init__(self):
        self.initial_change = 0
        
    def initial_decrease(self, output):
        m = re.match('.*Volume change by -([\d]*)', output)
        self.initial_change = int(m.groups(0)[0])
        return True

    def check_change(self, output, expected_ratio):
        if  expected_ratio > 0:
            r = '.*Volume change by ([\d]*)'
        else:
            r = '.*Volume change by -([\d]*)'
            expected_ratio = -expected_ratio
        m = re.match(r, output)
        if not m:
            print "Failure reason: Cannot interpret volume change"
            return False
        v = int(m.groups(0)[0])
        ratio = float(v)/float(self.initial_change)
        # Test within 15% tolerance
        if (ratio < expected_ratio - 0.15 or ratio > expected_ratio + 0.15):
            print "Failure reason: Volume change not as expected"
            return False
        return True

class VolumeInputTester(xmostest.Tester):

    def __init__(self):
            super(VolumeInputTester, self).__init__()

    def check_channel(self, analyzer_output, chan):
        EXPECTED_NUM_CHANGES = 5
        EXPECTED_INITIAL_VOL = 63
        result = True
        chan_output = []
        
        for line in analyzer_output:
            if line.startswith('Channel %d:' % chan):
                chan_output.append(line)
        if len(chan_output) != EXPECTED_NUM_CHANGES:
            print ("Failure reason: Unexpected number of lines of output seen for channel %d"
                   % chan)
            result = False
        else:
            volume_checker = VolumeChangeChecker()
            if not chan_output[0].startswith('Channel %d: Volume change by %d dB'
                                             % (chan, EXPECTED_INITIAL_VOL)):
                print ("Failure reason: Initial volume level of channel %d was not %ddB"
                       % (chan, EXPECTED_INITIAL_VOL))
                result = False
            if not volume_checker.initial_decrease(chan_output[1]):
                result = False
            if not volume_checker.check_change(chan_output[2], 1.0):
                result = False
            if not volume_checker.check_change(chan_output[3], -0.5):
                result = False
            if not volume_checker.check_change(chan_output[4], 0.5):
                result = False
        return result

    def run(self, dut_programming_output, sig_gen1_output, sig_gen2_output,
            sig_gen2_host_xscope_output, analyzer_output, vol_ctrl_output,
            os, app_name, app_config, num_chans, channel):
        result = True

        # Check for any errors
        for line in (dut_programming_output + sig_gen1_output + sig_gen2_output +
                     sig_gen2_host_xscope_output + analyzer_output):
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

        # Check that the signals were never lost
        for line in analyzer_output:
            if re.match('Channel [0-9]*: Lost signal', line):
                print "Failure reason: Signal lost detected"
                result = False

        # Check each channel transitions through the expected changes of volume
        if channel is 'master':
            for chan in range(num_chans):
                if not self.check_channel(analyzer_output, chan):
                    result = False
        else:
            # Check channel transitions through the expected changes of volume
            if not self.check_channel(analyzer_output, channel):
                result = False
            # Check all other channels have expected frequency
            for i in range(num_chans):
                if i == channel:
                    continue # Skip the channel having its volume changed
                found = False
                expected_freq = (i+1) * 1000
                expected_line = "Channel %d: Frequency %d" % (i, expected_freq)
                for line in analyzer_output:
                    if line.startswith(expected_line):
                        found = True
                if not found:
                    print ("Failure reason: Expected frequency of %d not seen on channel %d"
                           % (expected_freq, i))
                    result = False

        xmostest.set_test_result("sw_usb_audio",
                                 "analogue_hw_tests",
                                 "volume_input_test",
                                 config={'app_name':app_name,
                                        'num_chans':num_chans,
                                        'os':os,
                                        'app_config':app_config,
                                        'channel':channel},
                                 result=result,
                                 env={},
                                 output={'sig_gen1_output':''.join(sig_gen1_output),
                                         'sig_gen2_output':''.join(sig_gen2_output),
                                         'sig_gen2_host_xscope_output':''.join(sig_gen2_host_xscope_output),
                                         'analyzer_output':''.join(analyzer_output)})

def do_volume_input_test(board, os, app_name, app_config, freq, num_chans,
                         channel):
    duration = 20

    if channel is 'master':
        print ("Starting master volume input test on %s:%s under %s" %
               (app_name, app_config, os))
    else:
        print ("Starting volume input test of channel %d on %s:%s under %s" %
           (channel, app_name, app_config, os))

    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os))

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'

    ctester = xmostest.CombinedTester(6, VolumeInputTester(),
                                      os, app_name, app_config, num_chans, channel)

    if xmostest.get_testlevel() != 'smoke':
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
        if channel is 'master':
            xsig_config_file = "stereo_volcheck_in.m.json"
        else:
            xsig_config_file = "stereo_volcheck_in.%d.json" % channel
    else:
        if channel is 'master':
            xsig_config_file = "mc_volcheck_in.m.json"
        else:
            xsig_config_file = "mc_volcheck_in.%d.json" % channel
    analysis_job = xmostest.run_on_pc(resources['host'],
                                      [run_xsig_path,
                                      "%d" % (freq),
                                      "%d" % (duration * 1000), # xsig expects duration in ms
                                      "%s%s" % (xsig_configs_path, xsig_config_file)],
                                      tester = ctester[4],
                                      timeout = duration + 60, # xsig should stop itself gracefully
                                      initial_delay = 5,
                                      start_after_started = [sig_gen1_job, sig_gen2_job],
                                      start_after_completed = [dut_job])

    print "Scheduling PC volume control job"
    if os.startswith('os_x'):
        host_vol_ctrl_path = "../../../../usb_audio_testing/volcontrol/OSX/testvol_in.sh"
    elif os.startswith('win_'):
        host_vol_ctrl_path = "..\\..\\..\\..\\usb_audio_testing\\volcontrol\\win32\\testvol_in.bat"
    if channel is 'master':
        channel_number = 0
    else:
        channel_number = channel + 1
    volcontrol_job = xmostest.run_on_pc(resources['host_secondary'],
                                        [host_vol_ctrl_path,
                                        "%d" % (channel_number),
                                        "%d" % (num_chans+1)],
                                        tester = ctester[5],
                                        timeout = duration + 60, # testvol should stop itself
                                        initial_delay = 5,
                                        # start_after_started = [sig_gen1_job,
                                        #                        sig_gen2_job,
                                        #                        analysis_job],
                                        start_after_started = [analysis_job]
                                        # start_after_completed = [dut_job]
                                        )

def runtest():
    # key = friendly board name : values = 'app name', [(app config, input chan count, max sample freq, test level)...]...
    APP_NAME_OFFSET = 0
    CONFIG_LIST_OFFSET = 1
    CONFIG_NAME_OFFSET = 0
    CONFIG_CHAN_COUNT_OFFSET = 1
    CONFIG_MAX_SAMPLE_FREQ_OFFSET = 2
    CONFIG_TEST_LEVEL_OFFSET = 3
    tests = {
             'l2' : ('app_usb_aud_l2', [#('1ioxx', 2, 48000,
                                            #'nightly'), # FIXME: Doesn't work with Class 1.0 (no master vol, host app chan 0 usage...)
                                        ('2io_adatin', 6, 96000,
                                            'nightly'),
                                        ('2io_adatout', 6, 96000,
                                            'nightly'),
                                        ('2io_spdifout_adatout', 6, 96000,
                                            'nightly'),
                                        ('2io_spdifout_spdifin', 6, 192000,
                                            'nightly'),
                                        ('2io_spdifout_spdifin_mix8', 6, 192000,
                                            'nightly'),
                                        ('2io_tdm8', 6, 96000,
                                            'nightly'),
                                        ('2iomx', 6, 192000,
                                            'smoke'),
                                        ('2ioxs', 6, 192000,
                                            'smoke'),
                                        ('2ioxx', 6, 192000,
                                            'smoke')])
            }

    if xmostest.get_testlevel() != 'smoke':
        audio_boards = ['l2']
        host_oss = ['os_x', 'win_vista', 'win_7', 'win_8']
    else:
        # Smoke test only
        audio_boards = ['l2']
        host_oss = ['os_x']

    for board in audio_boards:
        app = tests[board][APP_NAME_OFFSET]
        for os in host_oss:
            for config in tests[board][CONFIG_LIST_OFFSET]:
                required_testlevel = config[CONFIG_TEST_LEVEL_OFFSET]
                if xmostest.testlevel_is_at_least(xmostest.get_testlevel(),
                                                  required_testlevel):
                    config_name = config[CONFIG_NAME_OFFSET]
                    num_chans = config[CONFIG_CHAN_COUNT_OFFSET]
                    max_freq = config[CONFIG_MAX_SAMPLE_FREQ_OFFSET]

                    # Test the master volume control
                    do_volume_input_test(board, os, app, config_name,
                                         max_freq, num_chans, 'master')

                    # Test the volume control of each channel
                    for chan in range(num_chans):
                        do_volume_input_test(board, os, app, config_name,
                                             max_freq, num_chans, chan)
