# Copyright (c) 2020, XMOS Ltd, All rights reserved

def pytest_addoption(parser):
    parser.addoption("--build-only", action="store_true")
    parser.addoption("--test-only", action="store_true")
