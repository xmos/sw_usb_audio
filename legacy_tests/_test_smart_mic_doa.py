#!/usr/bin/env python
import xmostest
import re
import os.path


class SmartMicTester(xmostest.Tester):
    # The SmartMicTester checks for errors reported by all of the processes run
    # during the test. If no errors are seen the test will be marked as a pass.


    def __init__(self, test, app_name, app_config, num_chans, sample_rate,
                 doa_dir, playback_file_name):
        super(SmartMicTester, self).__init__()
        self.product = "sw_usb_audio"
        self.group = "smart_mic_tests"
        self.test = test
        self.config = {'app_name':app_name,
                       'app_config':app_config,
                       'num_chans':num_chans,
                       'sample_rate':sample_rate,
                       'doa_dir':doa_dir,
                       'playback_file_name':playback_file_name,
                       }
        self.register_test(self.product, self.group, self.test, self.config)


    def record_failure(self, failure_reason):
        # Append a newline if there isn't one already
        if not failure_reason.endswith('\n'):
            failure_reason += '\n'
        self.failures.append(failure_reason)
        print ("Failure reason: %s" % failure_reason), # Print without newline
        self.result = False


    def run(self,
            dut_programming_job_output,
            control_job_output,
            dut_playback_record_job_output
            ):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_job_output
                     + control_job_output
                     + dut_playback_record_job_output
                     ):
            if re.match('.*ERROR|.*error|.*Error|.*Problem|.*ruined|could not',
                        line):
                self.record_failure(line)

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
            # Check DUT was flashed correctly
            found = False
            for line in dut_programming_job_output:
                if re.match('.*Site 0 has finished.*', line):
                    found = True
            if not found:
                self.record_failure("Expected xFLASH success message not seen")

        output = {'dut_programming_job_output':''.join(dut_programming_job_output),
                  'control_job_output':''.join(control_job_output),
                  'dut_playback_record_job_output':''.join(
                      dut_playback_record_job_output)
                  }
        if not self.result:
            output['failures'] = ''.join(self.failures)
        xmostest.set_test_result(self.product,
                                 self.group,
                                 self.test,
                                 self.config,
                                 self.result,
                                 env={},
                                 output=output)


xmostest_to_uac_path = os.path.join('..', '..', '..', '..')


def do_doa_test(min_testlevel, board, app_name, app_config, num_chans,
                sample_rate, doa_dir, playback_file_name):

    # Setup the tester which will determine and record the result
    tester = xmostest.CombinedTester(3, SmartMicTester("smart_mic_doa_test",
                                                       app_name, app_config,
                                                       num_chans,
                                                       sample_rate,
                                                       doa_dir,
                                                       playback_file_name))
    tester.set_min_testlevel(min_testlevel)

    # Get the hardware resources to run the test on
    resources = None
    try:
        resources = xmostest.request_resource("%s_testrig" % board, tester)
    except xmostest.XmosTestError:
        print "Unable to find required resources required to run test"
        tester.shutdown()
        return

    # Start the xCORE DUT
    dut_binary = os.path.join('..', app_name, 'bin', app_config, '%s_%s.xe' %
                              (app_name, app_config))
    if app_config.endswith('_xvsm2000'):
        env = {'XVSM':'1'}
    else:
        env = {}
    if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
        dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                       do_xe_prebuild = True,
                                       tester = tester[0],
                                       build_env = env)
    else:
        dut_job = xmostest.run_on_xcore(resources['dut'], dut_binary,
                                        do_xe_prebuild = True,
                                        tester = tester[0],
                                        disable_debug_io = True,
                                        build_env = env)

    # Start the control app
    ctrl_app_path = os.path.join(xmostest_to_uac_path, 'sw_usb_audio', 'tests',
                                 'smart_mic_config.py')
    control_job = xmostest.run_on_pc(resources['host_primary'],
                                     ['python', ctrl_app_path,
                                      'agc_on', '0',
                                      'doa_dir', str(doa_dir)],
                                     tester = tester[1],
                                     timeout = 1,
                                     initial_delay = 5,
                                     start_after_completed = [dut_job])

    # Start recording and playback on DUT
    uac_test_dir_path  = os.path.join(xmostest_to_uac_path, 'sw_usb_audio',
                                      'tests')
    player_recorder_path = os.path.join(uac_test_dir_path,
                                        'smart_mic_play_record.py')

    mic_data_file_name = os.path.join(uac_test_dir_path,
        'recording_%s_%s_doa_dir_%s.wav' % (app_config, playback_file_name, doa_dir))

    playback_file_path = os.path.join(uac_test_dir_path, 'test_audio',
                                      playback_file_name)
    dut_play_rec_job = xmostest.run_on_pc(resources['host_secondary'],
                                          ['python', player_recorder_path,
                                           playback_file_path,
                                           mic_data_file_name,
                                           str(sample_rate)],
                                          tester = tester[2],
                                          timeout = 300,
                                          initial_delay = 5,
                                          start_after_completed = [control_job])

    xmostest.complete_all_jobs()


def runtest():
    test_configs = [
        {'board':'mic_array', 'app':'app_usb_aud_mic_array',
         'app_configs':[
            {'config':'1i2o2_xvsm2000', 'chan_count':8,
             'testlevels':[
                {'level':'smoke',
                 'sample_rates':[16000],
                 'doa_dirs':[1, 2, 3, 4, 5, 6],
                 'playback_files':['oliver_twist.wav']},
                {'level':'nightly',
                 'sample_rates':[16000],
                 'doa_dirs':[1, 2, 3, 4, 5, 6],
                 'playback_files':['two_cities.wav']}
             ]
            },
         ]
        },
    ]

    args = xmostest.getargs()

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
                playback_files = run_type['playback_files']
                doa_dirs = run_type['doa_dirs']
                sample_rates = run_type['sample_rates']
                for pb_file in playback_files:
                    for direction in doa_dirs:
                        for sr in sample_rates:
                            do_doa_test(min_testlevel, board, app, config_name,
                                        num_chans, sr, direction, pb_file)
