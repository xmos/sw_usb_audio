# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
import subprocess
import re
from pathlib import Path
import yaml
import argparse
import shutil


def get_configs_from_cmake_output(cmake_cmd, app_dir):
    ret = subprocess.run(
            cmake_cmd, capture_output=True, text=True, cwd=app_dir
        )
    m = re.findall(r'-- Configuring application:.*?-- Adding dependency', ret.stdout, re.DOTALL)

    assert len(m) > 0, f"Couldn't parse cmake output for configs\n{ret.stdout}"
    output_dict = {}
    for app in m:
        app_name = app.splitlines()[0].split(':')[1].strip()
        configs = [f.split()[1].strip() for f in app.splitlines()[2:-1]]
        output_dict[app_name] = configs
    return output_dict


def main():
    parser = argparse.ArgumentParser(description="Parse build config names from cmake output")
    parser.add_argument('method', help='How to proceed.', choices=['check', 'update'])
    args = parser.parse_args()

    app_dir = Path(__file__).parents[3]
    config_dict = {}

    build_dir = Path(__file__).parent / "build_test"
    if build_dir.exists() and build_dir.is_dir():
        shutil.rmtree(build_dir)

    cmake_cmd = ["cmake", "-B", build_dir, "-S", app_dir]
    d = get_configs_from_cmake_output(cmake_cmd, build_dir.parent)
    for app, configs in d.items():
        config_dict[app] = {}
        config_dict[app]['full_configs'] = configs

    if build_dir.exists() and build_dir.is_dir():
        shutil.rmtree(build_dir)

    cmake_cmd = ["cmake", "-B", build_dir, "-S", app_dir, "-DPARTIAL_TESTED_CONFIGS=1"]
    d = get_configs_from_cmake_output(cmake_cmd, build_dir.parent)
    for app, configs in d.items():
        partial_configs = [c for c in configs if c not in config_dict[app]['full_configs']]
        assert app in config_dict
        config_dict[app]['partial_configs'] = partial_configs

    repo_file = app_dir / 'tests' / 'app_configs_autogen.yml' # File committed to the repository
    if args.method == 'update':
        with open(repo_file, 'w') as fp:
            yaml.dump(config_dict, fp)
    else: # check
        with open(repo_file) as fp:
            try:
                current_dict = yaml.safe_load(fp) # currently committed dictionary
                assert config_dict == current_dict, f"{repo_file} is out of date. Run <python tests/tools/app_configs_autogen/collect_configs.py update> from the sw_usb_audio directory to update"
                print(f"{repo_file} is up to date. No action required.")
            except yaml.YAMLError as exc:
                print(exc)
                assert False

if __name__ == "__main__":
    main()
