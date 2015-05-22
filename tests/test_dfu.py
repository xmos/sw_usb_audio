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
    ('r', "Firmware file '.*' successfully loaded\."),
    ('l', "Firmware download succeeded."),
    ('f', "00      0x20B1  {pid_str}  0x9901"),

    # Second upgrade
    ('r', "Firmware file '.*' successfully loaded\."),
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
    ('r', "Firmware file 'upload\.bin' successfully loaded\."),
    ('l', "Firmware download succeeded."),
    ('f', "00      0x20B1  {pid_str}  0x9902"),

    # Final factory revert
    ('l', "Reverting firmware to factory-default ..."),
    ('l', "Firmware revert succeeded ..."),
    ('f', "00      0x20B1  {pid_str}  {version_str}"),
]

class DFUTester(xmostest.Tester):

    def __init__(self):
        super(DFUTester, self).__init__()

    def run(self, dut_programming_output, upgrade_build_output, dfu_output,
            local_cleanup_output,
            # remote_cleanup_output,
            os, app_name, pid, app_config):
        result = True

        # Check for any errors
        for line in (dut_programming_output + upgrade_build_output + dfu_output):
            if re.match('.*ERROR|.*error|.*Error|.*Problem', line):
                print "Failure reason: Error message seen"
                result = False

        # Check cleanup worked
        for line in (local_cleanup_output): # TODO: Add + remote_cleanup_output
            if re.match('.*No such file|.*Stop', line):
                print "Failure reason: Post test cleanup did not succeed"
                result = False

        # Check DFU output is as expected
        if os.startswith('os_x'):
            expected_result = expected_osx
        elif os.startswith('win_'):
            expected_result = expected_win32

        starting_version = ''

        for expected in expected_result:
            line_mode = expected[0]
            expected_line = expected[1]

            if line_mode.count('f'):
                # Format the expected string before comparing
                expected_line = expected_line.format(version_str = starting_version, pid_str = pid)

            found = False
            for dfu_line in dfu_output:
                dfu_output = dfu_output[1:] # Remove each line as it's checked
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
                print ("Failure reason: Match for expected line not found, or not found in expected sequence...\n    Expected line: \"%s\""
                       % expected_line)
                result = False

        xmostest.set_test_result("sw_usb_audio",
                                 "non_audio_hw_tests",
                                 "dfu_test",
                                 config={'app_name':app_name,
                                        'os':os,
                                        'app_config':app_config},
                                 result=result,
                                 env={},
                                 output={'dfu_output':''.join(dfu_output)})

def do_dfu_test(board, os, app_name, pid, app_config):
    print ("Starting DFU test on %s:%s under %s" % (app_name, app_config, os))
    resources = xmostest.request_resource("uac2_%s_testrig_%s" % (board, os))

    dut_app_path = "../%s" % app_name
    dut_binary = ('%s/bin/%s/%s_%s.xe' %
                  (dut_app_path, app_config, app_name, app_config))

    ctester = xmostest.CombinedTester(4, DFUTester(), os, app_name, pid,
                                      app_config)

    print "Scheduling DUT flashing job"
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
    ctester[1].start_run()
    upgrade_job = schedule_job(cmd = ['bash', '-c', "%s" % cmd_string],
                               tester = ctester[1],
                               timeout = 600,
                               timeout_msg = "Building upgrade images timed out",
                               start_after_completed = [dut_job])

    print "Scheduling PC DFU job"
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
    ctester[3].start_run()
    cleanup_job = schedule_job(cmd = ['bash', '-c', "%s" % cmd_string],
                               tester = ctester[3],
                               timeout = 600,
                               timeout_msg = "Removing upgrade images timed out",
                               start_after_completed = [dfu_job])

    remote_cleanup_job = xmostest.run_on_pc(resources['host'],
                                            ["rm", "upload.bin"],
                                            # tester = ctester[4], # FIXME: locks up when output passed to tester
                                            timeout = 600,
                                            start_after_completed = [dfu_job])

def runtest():
    # key = friendly board name : values = 'app name', 'pid', [(app config, test level)...]...
    APP_NAME_OFFSET = 0
    PID_OFFSET = 1
    CONFIG_LIST_OFFSET = 2
    CONFIG_NAME_OFFSET = 0
    CONFIG_TEST_LEVEL_OFFSET = 1
    tests = {
             'l2' : ('app_usb_aud_l2', '0x0004', [('2io_adatin', 'nightly'),
                                                  ('2io_adatout', 'nightly'),
                                                  ('2io_spdifout_adatout', 'nightly'),
                                                  ('2io_spdifout_spdifin', 'nightly'),
                                                  ('2io_spdifout_spdifin_mix8', 'nightly'),
                                                  ('2io_tdm8', 'nightly'),
                                                  ('2iomx', 'smoke'),
                                                  ('2ioxs', 'smoke'),
                                                  ('2ioxx', 'smoke'),
                                                  ('2xoxs', 'smoke')])
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
        pid = tests[board][PID_OFFSET]
        for os in host_oss:
            for config in tests[board][CONFIG_LIST_OFFSET]:
                required_testlevel = config[CONFIG_TEST_LEVEL_OFFSET]
                if xmostest.testlevel_is_at_least(xmostest.get_testlevel(),
                                                  required_testlevel):
                    config_name = config[CONFIG_NAME_OFFSET]
                    do_dfu_test(board, os, app, pid, config_name)
