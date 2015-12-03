#!/usr/bin/env python
import xmostest
import re
import ntpath
import time

class SPDIFInputTester(xmostest.Tester):

    def __init__(self, app_name, app_config, spdif_base_chan, sample_rate,
                 duration, os, use_wdm):
        super(SPDIFInputTester, self).__init__()
        self.product = "sw_usb_audio"
        self.group = "digital_hw_tests"
        self.test = "spdif_input_test"
        self.config = {'app_name':app_name,
                       'app_config':app_config,
                       'spdif_base_chan':spdif_base_chan,
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

    def run(self, dut_programming_output, sig_gen_output, sig_gen_xscope_output, clock_set_output, analyzer_output):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + sig_gen_output + sig_gen_xscope_output + analyzer_output + clock_set_output):
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

        # Check that the signals detected follow the correct ramps
        expected_chan_step_sizes = [5, -7]
        for i, expected_step in enumerate(expected_chan_step_sizes):
            found = False
            expected_line = ("Channel %d: Ramp step = %d" %
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
                  'sig_gen_xscope_output': ''.join(sig_gen_xscope_output),
                  'clock_set_output': ''.join(clock_set_output),
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

def do_spdif_input_test(min_testlevel, board, app_name, app_config,
                        spdif_base_chan, sample_rate, duration, host_oss,
                        use_wdm=False):

    ctester = {}
    resources = {}
    dut_job = {}
    clock_select_job = {}
    sig_gen_job = {}
    analysis_job = {}

    for os in host_oss:

        ctester[os] = xmostest.CombinedTester(5, SPDIFInputTester(app_name, app_config,
                                                spdif_base_chan, sample_rate,
                                                duration, os, use_wdm))
        ctester[os].set_min_testlevel(min_testlevel)

        resources[os] = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                                ctester[os])
        time.sleep(0.01)

    dut_binary = ('../%s/bin/%s/%s_%s.xe' %
                  (app_name, app_config, app_name, app_config))

    analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_mc/bin/spdif_in/app_audio_analyzer_mc_spdif_in.xe'
    if board == 'xcore200_mc':
        analyser_binary = '../../sw_audio_analyzer/app_audio_analyzer_xcore200_mc/bin/spdif_test/app_audio_analyzer_xcore200_mc_spdif_test.xe'

    dep_dut_job = []

    for os in host_oss:

        if xmostest.testlevel_is_at_least(xmostest.get_testlevel(), 'weekend'):
            dut_job[os] = xmostest.flash_xcore(resources[os]['dut'], dut_binary,
                                              tester = ctester[os][0],
                                              start_after_completed = dep_dut_job)
            dep_dut_job.append(dut_job[os])
        else:
            dut_job[os] = xmostest.run_on_xcore(resources[os]['dut'], dut_binary,
                                            tester = ctester[os][0],
                                            disable_debug_io = True)

        # volcontrol app has the feature to switch clock source of the DUT
        if os.startswith('os_x'):
            host_vol_ctrl_path = "../../../../usb_audio_testing/volcontrol/volcontrol"
        elif os.startswith('win_'):
            host_vol_ctrl_path = "..\\..\\..\\..\\usb_audio_testing\\volcontrol\\win32\\volcontrol.bat"

        (analysis1_debugger_addr, analysis1_debugger_port) = resources[os]['analysis_device_1'].get_xscope_port().split(':')
        sig_gen_job[os] = xmostest.run_on_xcore(resources[os]['analysis_device_1'],
                                             analyser_binary,
                                             tester = ctester[os][1],
                                             enable_xscope = True,
                                             timeout = duration + 23, # Ensure signal generator runs for longer than audio analyzer
                                             start_after_completed = [dut_job[os]],
                                             xscope_host_cmd = ['../../sw_audio_analyzer/host_xscope_controller/bin/xscope_controller',
                                             analysis1_debugger_addr,
                                             analysis1_debugger_port,
                                             "%d" % (duration + 20),
                                             "f %d" % (sample_rate)],
                                             xscope_host_tester = ctester[os][2],
                                             xscope_host_timeout = duration + 60, # Host app should stop itself gracefully
                                             xscope_host_initial_delay = 6)

        # Signal generator should run, to have a valid SPDIF signal
        clock_select_job[os] = xmostest.run_on_pc(resources[os]['host_secondary'],
                                                [host_vol_ctrl_path, '--clock','SPDIF'],
                                                tester=ctester[os][3],
                                                timeout = 10,
                                                start_after_started = [sig_gen_job[os]],
                                                initial_delay = 10, # Needs atleast 7 seconds to get stable clock 
                                                )

        run_xsig_path = "../../../../xsig/xsig/bin/"
        xsig_configs_path = "../../../../usb_audio_testing/xsig_configs/"
        if os.startswith('os_x'):
            run_xsig_path += "run_xsig"
        elif os.startswith('win_'):
            run_xsig_path = ntpath.normpath(run_xsig_path) + "\\xsig"
            xsig_configs_path = ntpath.normpath(xsig_configs_path) + "\\"
        if spdif_base_chan is 0:
            xsig_config_file = "stereo_digital_input.json"
        else:
            xsig_config_file = "mc_digital_input.json"
            if board == 'xcore200_mc':
                xsig_config_file = "mc_digital_input_8ch.json"

        if use_wdm:
            wdm_arg = "--wdm"
        else:
            wdm_arg = ""
        analysis_job[os] = xmostest.run_on_pc(resources[os]['host'],
                                          [run_xsig_path,
                                          "%d" % (sample_rate),
                                          "%d" % (duration * 1000), # xsig expects duration in ms
                                          "%s%s" % (xsig_configs_path, xsig_config_file),
                                          wdm_arg],
                                          tester = ctester[os][4],
                                          timeout = duration + 60, # xsig should stop itself gracefully
                                          initial_delay = 5,
                                          start_after_started = [sig_gen_job[os]],
                                          start_after_completed = [dut_job[os], clock_select_job[os]])
        time.sleep(0.1)

    xmostest.complete_all_jobs()

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','app_configs':[
            {'config':'2io_spdifout_spdifin','spdif_base_chan':6,'testlevels':[
                {'level':'smoke','sample_rates':[192000]},
                {'level':'nightly','sample_rates':[176400]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000]}]},

            {'config':'2io_spdifout_spdifin_mix8','spdif_base_chan':6,'testlevels':[
                {'level':'nightly','sample_rates':[192000]},
                {'level':'weekend','sample_rates':[44100, 48000, 88200, 96000, 176400]}]},
            ]
        },
        {'board':'xcore200_mc','app':'app_usb_aud_xk_216_mc','app_configs':[

            {'config':'2i10o10xssxxx','spdif_base_chan':8,'testlevels':[
                {'level':'nightly','sample_rates':[44100, 48000, 192000]},
                {'level':'smoke','sample_rates':[48000]},
                {'level':'weekend','sample_rates':[88200, 96000, 176400]}]},
            ]
        }, 
    ]

    args = xmostest.getargs()

    host_oss = ['os_x_10', 'os_x_11', 'win_7', 'win_8', 'win_10']
    duration = 20

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
            spdif_base_chan = config['spdif_base_chan']
            for run_type in config['testlevels']:
                min_testlevel = run_type['level']
                sample_rates = run_type['sample_rates']
                for sample_rate in sample_rates:
                    do_spdif_input_test(min_testlevel, board, app,
                                        config_name, spdif_base_chan,
                                        sample_rate, duration, host_oss)

                # WDM test for SPDIF input might require different app build config?
                # win_oss = []
                # for os in host_oss:
                #     # Special case to test WDM on Windows
                #     # TODO: confirm WDM values are correct
                #     # FIXME: PortAudio error if WDM channel count is lower than spdif_base_chan
                #     WDM_SAMPLE_RATE = 44100
                #     if os.startswith('win_') and WDM_SAMPLE_RATE in sample_rates:
                #         win_oss.append(os)

                # do_spdif_input_test(min_testlevel, board, app,
                #                     config_name, spdif_base_chan,
                #                     WDM_SAMPLE_RATE, duration, win_oss,
                #                     use_wdm=True)
