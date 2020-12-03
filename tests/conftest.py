# Copyright (c) 2020, XMOS Ltd, All rights reserved

# This conftest.py is the smallest I could get away with
# To see how these args are used, look in tests/README.md

def pytest_addoption(parser):
    parser.addoption("--build-only", action="store_true")
    parser.addoption("--test-only", action="store_true")
