# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
import yaml
from pathlib import Path
import re

def test_version():
    pkg_dir = Path(__file__).parent
    settings_yaml_file = pkg_dir / ".." / "settings.yml"
    version_h_file = pkg_dir / ".." / "shared" / "version.h"

    with open(settings_yaml_file, 'r') as fp:
        # Get version from settings.yml
        settings_yml_version = yaml.safe_load(fp)['version']
        settings_yml_version = settings_yml_version.split(".")
        assert len(settings_yml_version) == 3

        # Get version from version.h
        with open(version_h_file, 'r') as f_conf:
            data = f_conf.read()
            # Parse BCD version numbers from version.h
            m = (re.findall(r"#define\s+(BCD_DEVICE_[JMN])\s+\((\d+)\)", data, flags=re.MULTILINE))
            assert len(m) == 3
            bcd_version = {i[0]:i[1] for i in m}
            fail = False
            if bcd_version['BCD_DEVICE_J'] != settings_yml_version[0]:
                print(f"Error: BCD_DEVICE_J between version.h ({bcd_version['BCD_DEVICE_J']}) and settings.yml ({settings_yml_version[0]}) doesn't match")
                fail = True

            if bcd_version['BCD_DEVICE_M'] != settings_yml_version[1]:
                print(f"Error: BCD_DEVICE_M between version.h ({bcd_version['BCD_DEVICE_M']}) and settings.yml ({settings_yml_version[1]}) doesn't match")
                fail = True

            if bcd_version['BCD_DEVICE_N'] != settings_yml_version[2]:
                print(f"Error: BCD_DEVICE_N between version.h ({bcd_version['BCD_DEVICE_N']}) and settings.yml ({settings_yml_version[2]}) doesn't match")
                fail = True

            assert fail == False, f"Version mismatch between settings.yml ({settings_yml_version}) and version.h ({bcd_version})"

if __name__ == "__main__":
    test_version()


