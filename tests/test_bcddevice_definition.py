#!/usr/bin/env python
import xmostest
from sourcepackaging import get_lib_version
import os
import re
import collections

def runtest():
    # Get the current version number
    version = get_lib_version("../../sw_usb_audio/", use_only_changelog=True)

    # Decompose version number into J, M, and N values
    j_m_n = version.split('.')

    expected_output = ["BCD_DEVICE_J defined as "+j_m_n[0],
                       "BCD_DEVICE_M defined as "+j_m_n[1],
                       "BCD_DEVICE_N defined as "+j_m_n[2]]

    tester = xmostest.ComparisonTester(expected_output,
                                       "sw_usb_audio",
                                       "sw_release_tests",
                                       "usb_descriptor_bcddevice_definition")

    bcdDevice_search_results = collections.OrderedDict()
    bcdDevice_search_results['J'] = {'Values':[],'Files':[]}
    bcdDevice_search_results['M'] = {'Values':[],'Files':[]}
    bcdDevice_search_results['N'] = {'Values':[],'Files':[]}

    # Check the whole sandbox, not just this repo
    root_of_search = os.path.join('..','..')
    for dirpath, dirnames, files in os.walk(root_of_search):
        # Filter out directories that won't contain source files of interest
        dirnames_copy = dirnames[:]
        for dir in dirnames_copy:
            if (dir.startswith('.') or
                dir.startswith('_build') or
                dir.startswith('Installs') or
                dir.startswith('tools_') or
                dir.startswith('infr_') or
                dir.startswith('xdoc_released') or
                dir.startswith('fftw') or
                dir.startswith('portaudio') or
                dir.startswith('xsig')):
                dirnames.remove(dir)
        # Search for bcdDevice defines in the source files
        for filename in files:
            with open(os.path.join(dirpath, filename), 'r') as f:
                for line in f:
                    m = re.match('\s*#define\s+BCD_DEVICE_(J|M|N)\s+(\d+)',
                                 line)
                    if m:
                        # Found a line containing a bcdDevice define
                        define_name = m.group(1)
                        define_value = m.group(2)

                        # Record the value found
                        bcdDevice_search_results[define_name]['Values'].append(
                            define_value)
                        bcdDevice_search_results[define_name]['Files'].append(
                            os.path.abspath(os.path.join(dirpath, filename)))

    # Format the recorded values in the required test output
    test_output = []
    for name in bcdDevice_search_results:
        count = len(bcdDevice_search_results[name]['Values'])
        if count is 1:
            test_output.append("BCD_DEVICE_"+name+" defined as "+
                               str(bcdDevice_search_results[name]['Values'][0]))
        elif count > 1:
            failures = ["Found multiple defines for BCD_DEVICE_"+name]
            for i in range(0, count):
                value = str(bcdDevice_search_results[name]['Values'][i])
                filepath = bcdDevice_search_results[name]['Files'][i]
                failures.append("\nBCD_DEVICE_"+name+" defined as "+value+
                                " in "+filepath)
            test_output.append(''.join(failures))

    # Test for a match
    tester.run(test_output)
