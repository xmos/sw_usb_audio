#!/usr/bin/env python
import xmostest
import re
import ntpath

class AnalogueInputTester(xmostest.Tester):

    def __init__(self):
            super(AnalogueInputTester, self).__init__()

    def run(self, dut_programming_output, sig_gen1_output,
            sig_gen2_output, sig_gen2_host_xscope_output, analyzer_output,
            os, app_name, app_config, freq, duration, num_chans, use_wdm):
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

        # Check that the signals detected are of the correct frequencies
        for i in range(num_chans):
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

        for line in analyzer_output:
            # Check that the signals were never lost
            if re.match('Channel [0-9]*: Lost signal', line):
                print "Failure reason: Signal lost detected"
                result = False
            # Check that unexpected signals are not detected
            if re.match('Channel [0-9]*: Signal detected .*', line):
                chan_num = int(re.findall('\d', line)[0])
                if chan_num not in range(0, num_chans):
                    print ("Failure reason: Unexpected signal detected on channel %d"
                           % chan_num)
                    result = False
            if re.match('Channel [0-9]*: Frequency [0-9]* .*', line):
                chan_num = int(re.findall('\d', line)[0])
                if chan_num not in range(0, num_chans):
                    print ("Failure reason: Unexpected frequency reported on channel %d"
                           % chan_num)
                    result = False

        xmostest.set_test_result("sw_usb_audio",
                                 "analogue_hw_tests",
                                 "analogue_input_test",
                                 config={'app_name':app_name,
                                        'num_chans':num_chans,
                                        'duration':duration,
                                        'os':os,
                                        'use_wdm':use_wdm,
                                        'app_config':app_config,
                                        'freq':freq},
                                 result=result,
                                 env={},
                                 output={'sig_gen1_output':''.join(sig_gen1_output),
                                         'sig_gen2_output':''.join(sig_gen2_output),
                                         'sig_gen2_host_xscope_output':''.join(sig_gen2_host_xscope_output),
                                         'analyzer_output':''.join(analyzer_output)})

def do_analogue_input_test(board, os, app_name, app_config, freq, duration,
                           num_chans, use_wdm=False):
    print ("Starting analogue input test at %d on %s:%s under %s" %
           (freq, app_name, app_config, os))
    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os))

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/app_audio_analyzer_mc.xe'

    ctester = xmostest.CombinedTester(5, AnalogueInputTester(),
                                      os, app_name, app_config, freq, duration,
                                      num_chans, use_wdm)

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
                                      "%d" % (freq),
                                      "%d" % (duration * 1000), # xsig expects duration in ms
                                      "%s%s" % (xsig_configs_path, xsig_config_file),
                                      wdm_arg],
                                      tester = ctester[4],
                                      timeout = duration + 60, # xsig should stop itself gracefully
                                      initial_delay = 5,
                                      start_after_started = [sig_gen1_job, sig_gen2_job],
                                      start_after_completed = [dut_job])

def runtest():
    # key = friendly board name : values = 'app name', [(app config, input chan count, [sample freqs...], test level)...]
    APP_NAME_OFFSET = 0
    CONFIG_LIST_OFFSET = 1
    CONFIG_NAME_OFFSET = 0
    CONFIG_CHAN_COUNT_OFFSET = 1
    CONFIG_SAMPLE_FREQS_OFFSET = 2
    CONFIG_TEST_LEVEL_OFFSET = 3
    tests = {
             'l2' : ('app_usb_aud_l2', [('1ioxx', 2,
                                            [44100, 48000],
                                            'smoke'),
                                        ('2io_adatin', 6,
                                            [44100, 48000, 88200, 96000],
                                            'nightly'), #FIXME: not working at 176400 or 192000
                                        ('2io_adatout', 6,
                                            [44100, 48000, 88200, 96000],
                                            'nightly'),
                                        ('2io_spdifout_adatout', 6,
                                            [44100, 48000, 88200, 96000],
                                            'nightly'),
                                        ('2io_spdifout_spdifin', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'nightly'),
                                        ('2io_spdifout_spdifin_mix8', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'nightly'), # FIXME: Regularly failing test
                                        ('2io_tdm8', 6,
                                            [44100, 48000, 88200, 96000],
                                            'nightly'),
                                        ('2iomx', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'smoke'),
                                        ('2ioxs', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'smoke'),
                                        ('2ioxx', 6,
                                            [44100, 48000, 88200, 96000, 176400, 192000],
                                            'smoke')])
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
                    num_chans = config[CONFIG_CHAN_COUNT_OFFSET]
                    sample_freqs = config[CONFIG_SAMPLE_FREQS_OFFSET]

                    for freq in sample_freqs:
                        if freq in test_freqs:
                            do_analogue_input_test(board, os, app, config_name,
                                                   freq, duration, num_chans)

                    # Special case to test WDM on Windows
                    # TODO: confirm WDM values are correct
                    WDM_SUPPORTED_FREQ = 44100
                    WDM_MAX_NUM_CHANS = 2
                    if os.startswith('win_') and WDM_SUPPORTED_FREQ in sample_freqs:
                        do_analogue_input_test(board, os, app, config_name,
                                               WDM_SUPPORTED_FREQ, duration,
                                               WDM_MAX_NUM_CHANS, use_wdm=True)
