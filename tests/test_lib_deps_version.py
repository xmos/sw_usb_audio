#!/usr/bin/env python
import xmostest
from sourcepackaging import get_lib_version, findXCoreApps, get_app_dependencies
import os
import re
import collections
from xmos_subprocess import call_get_output

def runtest():
    # Get the current version number
    apps = findXCoreApps("../../sw_usb_audio/", include_tests = False)
    deps = []
    msg = ''
    result = 'PASS'

    xmostest.register_test("sw_usb_audio", "sw_release_tests", "lib_deps_version", {})

    # Gather all the dependencies from all apps
    for app in apps:
        deps.extend(get_app_dependencies(app))

    # Remove duplicates
    deps = list(set(deps))

    version_str_regex = '^(v)(\d+\.)(\d+\.)(\d+)(.*)$'

    # Iterate through the deps and check if the HEAD in git is tagged
    for dep_path in deps:
        dep_name = os.path.basename(os.path.normpath(dep_path))
        msg += "Checking %s\n" % dep_name
        (stdout, stderr) = call_get_output(["git","tag","--points-at", "HEAD"], cwd = dep_path)

        if stderr: 
            msg += stderr[0]
            msg += "ERROR: Dependency %s is not tagged (not a released version?)\n" % dep_name
            result = 'FAIL'
            continue
        if not stdout: 
            msg += "ERROR: Dependency %s is not tagged (not a released version?)\n" % dep_name
            result = 'FAIL'
            continue

        for stdo in stdout:
            if re.match(version_str_regex, stdo):
                tag = stdo.rstrip() # Remove newline
                tag_without_v = tag[1:]  # Remove character 'v' from tag
                tag_without_v = re.sub('rc\d*','',tag_without_v) # Remove 'rc' from end of tag
                version = get_lib_version(dep_path)

                if version == tag_without_v:
                    msg += "OK\n"
                else:
                    msg += "ERROR: Dependency %s git tag implies version '%s' but lib version is set to '%s'\n" % (dep_name, tag_without_v, version) 
                    result = 'FAIL'
            #else:
             #   msg += "ERROR: Dependency %s is tagged but the tag '%s' doesn't look like a version number\n" % (dep_name, stdout[0].rstrip())
              #  result = 'FAIL'

    xmostest.set_test_result("sw_usb_audio", "sw_release_tests", "lib_deps_version", {}, result, output = msg)
