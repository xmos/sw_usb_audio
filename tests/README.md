How to run and extend these tests
=================================

To run the tests, **you will need a USB audio regression test rig.** This is a
rig with two stacked multi-channel audio boards. You will need to connect them
to xTags and map the xtags for use with xtagctl. For more info on how to set
this up, see the README in the xtagctl repo.

These tests are written using pytest combined with xtagctl

To build all firmware required to run these tests, use:
```
$ pytest --build-only -n 1
```

To run all the tests without re-building firmware, use:
```
$ pytest --test-only
```

To build everything, then test, run without any arguments:
```
$ pytest -n 1
```

**NOTE:** The `-n 1` prevents xmake from running in parallel. xtagctl is
designed to handle parallel execution, so running multiple executors in
`--test-only` mode is OK.

Adding a test
-------------

To allow each test to build the config it needs, we make heavy use of pytest
fixtures.

To add a board/config to a test, look for the 
``` python
@pytest.mark.parametrize("build", ..., indirect=True)
```
line above the test definition.

For DFU tests, look for:
``` python
@pytest.mark.parametrize("build_with_dfu", ..., indirect=True)
```

Debugging
=========

By default, the tests will log to a test.log file. Use the following command to
monitor test output while the tests are running:

```
tail -n 50 -f test.log
```

Troubleshooting
===============

## FT232H Error

```
>           raise XtagctlFt232hException(f"FT232H error: {e}")
E           xtagctl.exceptions.XtagctlFt232hException: FT232H error: The device has no langid (permission issue, no string descriptors supported or device error)
```

This can be solved by either:

- Ensuring you have the correct rules in /etc/udev/rules.d (See FT232H
  Configuration in the xtagctl repo)
- Power Cycling the FT232H - this may be necessary after a reboot

## Could not find device

Under Linux, some USB hubs/docks can fail when there's too much USB activity.
Make sure the hardware is connected across as many ports as possible on the USB
host machine.
