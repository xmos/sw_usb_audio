#!/usr/bin/env python
import sys
import os.path
import subprocess

if __name__ == '__main__':
    ctrl_app_path = os.path.join('..', '..', '..', '..', 'lib_xvsm_support',
                                 'host', 'bin', 'xvsm_usb')

    # Run xvsm_usb with each of the arguments given
    # Skip argv[0] which contains name of this script
    # Assume all arguments are given as arg_name value pairs
    for val, arg in enumerate(sys.argv[1::2], 1):
        # enumerate() doesn't account for list step size, so must use val * 2
        subprocess.call([ctrl_app_path, arg, str(sys.argv[val*2])])
