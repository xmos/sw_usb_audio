#!/usr/bin/env python
import xmostest

class SmartMicTester(xmostest.Tester):
    # The SmartMicTester checks for errors reported by all of the processes run
    # during the test. If no errors are seen the test will be marked as a pass.

    def __init__(self, test, app_name, app_config, num_chans):
        super(SmartMicTester, self).__init__()
        self.product = "sw_usb_audio"
        self.group = "smart_mic_tests"
        self.test = test
        self.config = {'app_name':app_name,
                       'app_config':app_config,
                       'num_chans':num_chans}
        self.register_test(self.product, self.group, self.test, self.config)

    def run(self,
            dut_programming_job_output,
            generator_job_output,
            control_job_output,
            extern_sound_job_output,
            dut_playback_record_job_output,
            result_analysis_job_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_job_output + generator_job_output +
                     control_job_output + extern_sound_job_output +
                     dut_playback_record_job_output + result_analysis_job_output):
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
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
                  'generator_job_output':''.join(generator_job_output),
                  'control_job_output':''.join(control_job_output),
                  'extern_sound_job_output':''.join(extern_sound_job_output),
                  'dut_playback_record_job_output':''.join(
                      dut_playback_record_job_output),
                  'result_analysis_job_output':''.join(result_analysis_job_output)}
        if not self.result:
            output['failures'] = ''.join(self.failures)
        xmostest.set_test_result(self.product,
                                 self.group,
                                 self.test,
                                 self.config,
                                 self.result,
                                 env={},
                                 output=output)

# TODO: remove these strings
path_to_gen_app = path_to_ctrl_app = path_to_ext_player = path_to_mic_player = path_to_analysis_app = 'echo'
gen_arg1 = gen_arg2 = ctrl_arg1 = ctrl_arg2 = player_arg1 = player_arg2 = analysis_arg1 = analysis_arg2 = 'hello'

# TODO: rename for specific test case
def do_smart_mic_test(min_testlevel, board, app_name, app_config, num_chans):

    # Setup the tester which will determine and record the result
    tester = xmostest.CombinedTester(6, SmartMicTester("smart_mic_test", # TODO: rename for specific test case
                                                       app_name, app_config,
                                                       num_chans))
    tester.set_min_testlevel(min_testlevel)

    # Get the hardware resources to run the test on
    resources = xmostest.request_resource("%s_testrig" % board, tester)

    # TODO: run calibration jobs

    # Start the xCORE DUT
    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))
    # FIXME: DUT binary must currently be built before running tests
    # if app_config.endswith('_xvsm2000'):
    #     env = {'XVSM':'1'}
    # else:
    #     env = {}
    if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
        dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                       do_xe_prebuild = False, # FIXME
                                       tester = tester[0])
    else:
        dut_job = xmostest.run_on_xcore(resources['dut'], dut_binary,
                                        do_xe_prebuild = False, # FIXME
                                        tester = tester[0],
                                        disable_debug_io = True)
                                        # build_env = env) TODO: fix or remove

    # Run sound file generator
    generator_job = xmostest.run_on_pc(resources['host_primary'],
                                       [path_to_gen_app, gen_arg1, gen_arg2],
                                       tester = tester[0],
                                       timeout = 1, # TODO: set this
                                       initial_delay = 0) # TODO: set this

    # Start the control app
    control_job = xmostest.run_on_pc(resources['host_primary'],
                                     [path_to_ctrl_app, ctrl_arg1, ctrl_arg2],
                                     tester = tester[0],
                                     timeout = 1, # TODO: set this
                                     initial_delay = 0, # TODO: set this
                                     start_after_completed = [dut_job,
                                                              generator_job])

    # Start the external sound playback
    ext_player_job = xmostest.run_on_pc(resources['host_secondary'],
                                        [path_to_ext_player, player_arg1, player_arg2],
                                        tester = tester[0],
                                        timeout = 1, # TODO: set this
                                        initial_delay = 0, # TODO: set this
                                        start_after_started = [control_job])

    # Start recording (and playback) on DUT
    dut_play_rec_job = xmostest.run_on_pc(resources['host_tertiary'],
                                          [path_to_mic_player, player_arg1, player_arg2],
                                          tester = tester[0],
                                          timeout = 1, # TODO: set this
                                          initial_delay = 0, # TODO: set this
                                          start_after_started = [control_job])

    # Once all test jobs have completed run the analysis application
    xmostest.run_on_pc(resources['host_primary'],
                       [path_to_analysis_app, analysis_arg1, analysis_arg2],
                       tester = tester[0],
                       timeout = 1,
                       start_after_completed = [control_job, ext_player_job,
                                                dut_play_rec_job]) # TODO: set this

    xmostest.complete_all_jobs()

def runtest():
    test_configs = [
        {'board':'mic_array','app':'app_usb_aud_mic_array','app_configs':[
            {'config':'1i2o2_xvsm2000','chan_count':8,'testlevels':[
                # TODO: Add desired config for each test level to these dictionaries
                {'level':'smoke'},
                {'level':'nightly'},
                {'level':'weekend'}]},

            {'config':'2i8o2','chan_count':8,'testlevels':[
                # TODO: Add desired config for each test level to these dictionaries
                {'level':'smoke'},
                {'level':'nightly'},
                {'level':'weekend'}]},

            {'config':'1i8o2','chan_count':8,'testlevels':[
                # TODO: Add desired config for each test level to these dictionaries
                {'level':'smoke'},
                {'level':'nightly'},
                {'level':'weekend'}]}
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
                do_smart_mic_test(min_testlevel, board, app, config_name,
                                  num_chans)
                # TODO: run other smart mic tests here
