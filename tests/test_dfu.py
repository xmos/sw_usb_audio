#!/usr/bin/env python
import xmostest
import re
from xmostest.jobs import schedule_job

# Matching modes:
# l = Match line with string compare
# r = Match line with regex
# f = Format the string replacing the values within {curly braces}
# x = Regex containing capturing groups to extract values
#
# Can be combined by providing a list of modes, e.g. ['f','x']
# Be careful to avoid creating dependencies between extracted values and
# values used for string formatting, no sanity checking for this is included.

expected_osx = [
    # Check initial version
    ('l', "DFU test"),
    ('l', "Version Read:"),
    ('x', "\s(Version):\s+([0-9a-fA-F]{1,2}\.[0-9a-fA-F]{1,2})"),

    # First upgrade
    ('r', "... Downloading image \(.*\) to device"),
    ('l', "Version Read:"),
    ('r', "\s+Version: 99.01"),

    # Second upgrade
    ('r', "... Downloading image \(.*\) to device"),
    ('l', "Version Read:"),
    ('r', "\s+Version: 99.02"),

    # Read out upgrade image from device
    ('l', "*** DFU upload existing firmware ***"),
    ('l', "... Uploading image (upload.bin) from device"),
    ('l', "Version Read:"),
    ('r', "\s+Version: 99.02"),

    # Factory revert
    ('l', "... Reverting device to factory image"),
    ('l', "... Returning device to application mode"),
    ('l', "Version Read:"),
    (['f','r'], "\s+Version: {version_str}"),

    # Download the uploaded image back to the device
    ('l', "... Downloading image (upload.bin) to device"),
    ('l', "Version Read:"),
    ('r', "\s+Version: 99.02"),

    # Final factory revert
    ('l', "... Reverting device to factory image"),
    ('l', "Version Read:"),
    (['f','r'], "\s+Version: {version_str}"),

    ('l', "DFU Test Complete!")
]

expected_win32 = [
    # Check initial version
    (['f','x'], "00\s+(0x20B1)\s+{pid_str}\s+(0x[0-9a-fA-F]{{1,4}}).*"),

    # First upgrade
    ('r', "Downloading .* to target \d+ \.\.\."),
    ('l', "Firmware download succeeded."),
    ('f', "00      0x20B1  {pid_str}  0x9901"),

    # Second upgrade
    ('r', "Downloading .* to target \d+ \.\.\."),
    ('l', "Firmware download succeeded."),
    ('f', "00      0x20B1  {pid_str}  0x9902"),

    # Read out upgrade image from device
    ('l', "Firmware upload started ..."),
    ('l', "Firmware upload finished."),
    ('r', "Uploaded firmware image \(\d+ bytes\) written to upload\.bin\."),

    # Factory revert
    ('l', "Reverting firmware to factory-default ..."),
    ('l', "Firmware revert succeeded ..."),
    ('f', "00      0x20B1  {pid_str}  {version_str}"),

    # Download the uploaded image back to the device
    ('r', "Downloading upload.bin to target \d+ \.\.\."),
    ('l', "Firmware download succeeded."),
    ('f', "00      0x20B1  {pid_str}  0x9902"),

    # Final factory revert
    ('l', "Reverting firmware to factory-default ..."),
    ('l', "Firmware revert succeeded ..."),
    ('f', "00      0x20B1  {pid_str}  {version_str}"),
]

class DFUTester(xmostest.Tester):

    def __init__(self, app_name, app_config, os):
        super(DFUTester, self).__init__()
        self.product = "sw_usb_audio"
        self.group = "non_audio_hw_tests"
        self.test = "dfu_test"
        self.config = {'app_name':app_name,
                       'app_config':app_config,
                       'os':os}
        self.register_test(self.product, self.group, self.test, self.config)

    def record_failure(self, failure_reason):
        # Append a newline if there isn't one already
        if re.match('.*\n', failure_reason) is None:
            failure_reason += '\n'
        self.failures.append(failure_reason)
        print ("Failure reason: %s" % failure_reason), # Print without newline
        self.result = False

    def run(self, dut_programming_output, upgrade_build_output, dfu_output,
            local_cleanup_output,
            # remote_cleanup_output,
            pid):
        self.result = True
        self.failures = []

        # Check for any errors
        for line in (dut_programming_output + upgrade_build_output + dfu_output +
                     local_cleanup_output): # TODO: Add + remote_cleanup_output
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
                self.record_failure(line)

        # Check DUT was flashed correctly
        found = False
        for line in dut_programming_output:
            if re.match('.*Site 0 has finished.*', line):
                found = True
        if not found:
            self.record_failure("Expected xFLASH success message not seen")

        # Check cleanup worked
        for line in (local_cleanup_output): # TODO: Add + remote_cleanup_output
            if re.match('.*No such file|.*Stop', line):
                self.record_failure("Post test cleanup did not succeed\n%s" % line)

        # Check DFU output is as expected
        if self.config['os'].startswith('os_x'):
            expected_result = expected_osx
        elif self.config['os'].startswith('win_'):
            expected_result = expected_win32

        starting_version = ''

        for expected in expected_result:
            line_mode = expected[0]
            expected_line = expected[1]

            if line_mode.count('f'):
                # Format the expected string before comparing
                expected_line = expected_line.format(version_str = starting_version, pid_str = pid)

            found = False
            # Original output included in results, so create a copy to modify
            dfu_output_scratch = dfu_output
            for dfu_line in dfu_output_scratch:
                dfu_output_scratch = dfu_output_scratch[1:] # Remove each line as it's checked
                if line_mode.count('x'):
                    # Extract values from output
                    extracted_vals = re.split(expected_line, dfu_line)
                    if (len(extracted_vals) == 4 and
                        (extracted_vals[1] == 'Version' or
                         extracted_vals[1] == '0x20B1')):
                        starting_version = extracted_vals[2]
                        found = True
                        break
                elif line_mode.count('r'):
                    # Match line as regex
                    if re.match(expected_line, dfu_line):
                        found = True
                        break
                else:
                    # Match line as string
                    if dfu_line.startswith(expected_line):
                        found = True
                        break
            if not found:
                self.record_failure("Match for expected line not found, or not found in expected sequence...\n    Expected line: \"%s\""
                                    % expected_line)

        output = {'dfu_output':''.join(dfu_output)}
        if not self.result:
            output['failures'] = ''.join(self.failures)
        xmostest.set_test_result(self.product,
                                 self.group,
                                 self.test,
                                 self.config,
                                 self.result,
                                 env={},
                                 output=output)

def do_dfu_test(min_testlevel, board, app_name, pid, app_config, os):

    ctester = xmostest.CombinedTester(4, DFUTester(app_name, app_config, os),
                                      pid)
    ctester.set_min_testlevel(min_testlevel)

    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os),
                                          ctester)

    dut_app_path = "../%s" % app_name
    dut_binary = ('%s/bin/%s/%s_%s.xe' %
                  (dut_app_path, app_config, app_name, app_config))

    dut_job = xmostest.flash_xcore(resources['dut'], dut_binary,
                                   tester = ctester[0])

    xflash_cmds = ['cd %s;' % dut_app_path,
                   'xmake clean CONFIG=%s;' % app_config,
                   'xmake CONFIG=%s TEST_DFU_1=1;' % app_config,
                   'xflash --factory-version 13.2 --upgrade 1 bin/%s/%s_%s.xe 0x10000 -o upgrade1.bin --verbose;' % (app_config, app_name, app_config),
                   'xmake clean CONFIG=%s;' % app_config,
                   'xmake CONFIG=%s TEST_DFU_2=1;' % app_config,
                   'xflash --factory-version 13.2 --upgrade 2 bin/%s/%s_%s.xe 0x10000 -o upgrade2.bin --verbose' % (app_config, app_name, app_config)]
    cmd_string = " ".join([x for x in xflash_cmds])

    # Scheduled as a job to delay building upgrades until dut_job has completed
    upgrade_job = []
    if xmostest.testrun_is_required(ctester[1]):
        ctester[1].start_run()
        upgrade_job = schedule_job(cmd = ['bash', '-c', "%s" % cmd_string],
                                   tester = ctester[1],
                                   timeout = 600,
                                   timeout_msg = "Building upgrade images timed out",
                                   start_after_completed = [dut_job])

    if os.startswith('os_x'):
        host_dfu_path = "../../../../usb_audio_testing/dfu/OSX/testdfu.sh"
    elif os.startswith('win_'):
        host_dfu_path = '"..\\..\\..\\..\\usb_audio_testing\\dfu\\win32\\testdfu.bat "C:\\Program Files\\Thesycon\\TUSBAudio_Driver\\dfucons.exe""'
    dfu_job = xmostest.run_on_pc(resources['host'],
                                 ["%s" % host_dfu_path, "<remote_file>", "<remote_file>"],
                                 files_used_as_args = ['%s/upgrade1.bin' % dut_app_path, '%s/upgrade2.bin' % dut_app_path],
                                 tester = ctester[2],
                                 timeout = 600,
                                 start_after_completed = [dut_job, upgrade_job])

    # Clean up upgrade images created
    cleanup_cmds = ['cd %s;' % dut_app_path,
                    'xmake clean CONFIG=%s;' % app_config,
                    'rm upgrade1.bin upgrade2.bin;',
                    'xmake CONFIG=%s' % app_config]
    cmd_string = " ".join([x for x in cleanup_cmds])

    if xmostest.testrun_is_required(ctester[3]):
        ctester[3].start_run()
        cleanup_job = schedule_job(cmd = ['bash', '-c', "%s" % cmd_string],
                                   tester = ctester[3],
                                   timeout = 600,
                                   timeout_msg = "Removing upgrade images timed out",
                                   start_after_completed = [dfu_job])

        if os.startswith('os_x'):
            remote_cleanup_cmd = ["rm", "upload.bin"]
        elif os.startswith('win_'):
            remote_cleanup_cmd = ["del", "upload.bin"]
        remote_cleanup_job = xmostest.run_on_pc(resources['host'],
                                                remote_cleanup_cmd,
                                                # tester = ctester[4], # FIXME: locks up when output passed to tester
                                                timeout = 600,
                                                start_after_completed = [dfu_job])

def runtest():
    test_configs = [
        {'board':'l2','app':'app_usb_aud_l2','pid':'0x0004','app_configs':[
            {'config':'2io_adatin','testlevel':'nightly'},
            {'config':'2io_adatout','testlevel':'nightly'},
            {'config':'2io_spdifout_adatout','testlevel':'nightly'},
            {'config':'2io_spdifout_spdifin','testlevel':'nightly'},
            {'config':'2io_spdifout_spdifin_mix8','testlevel':'nightly'},
            {'config':'2io_tdm8','testlevel':'nightly'},
            {'config':'2iomx','testlevel':'smoke'},
            {'config':'2ioxs','testlevel':'smoke'},
            {'config':'2ioxx','testlevel':'smoke'},
            {'config':'2xoxs','testlevel':'smoke'}
            ]
        }
    ]

    host_oss = ['os_x_10', 'os_x_11', 'win_7', 'win_8', 'win_10']

    for test in test_configs:
        board = test['board']
        app = test['app']
        pid = test['pid']
        for os in host_oss:
            for config in test['app_configs']:
                config_name = config['config']
                min_testlevel = config['testlevel']
                do_dfu_test(min_testlevel, board, app, pid, config_name, os)
