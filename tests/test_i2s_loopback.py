#!/usr/bin/env python
import xmostest

def runtest_one_config(config):
    testlevel = 'smoke'
    resources = xmostest.request_resource('xsim')

    binary = 'i2s_loopback/bin/{config}/i2s_loopback_{config}.xe'.format(config=config)
    tester = xmostest.ComparisonTester(open('pass.expect'),
                                       'sw_usb_audio',
                                       'sc_usb_audio_tests',
                                       'i2s_loopback',
                                       {'config': config})
    tester.set_min_testlevel(testlevel)
    xmostest.run_on_simulator(resources['xsim'], binary, tester=tester,
                              simargs=['--plugin', 'LoopbackPort.dll',
                                '-port tile[0] XS1_PORT_1M 1 0 -port tile[0] XS1_PORT_1I 1 0 ' +
                                '-port tile[0] XS1_PORT_1N 1 0 -port tile[0] XS1_PORT_1J 1 0 ' +
                                '-port tile[0] XS1_PORT_1O 1 0 -port tile[0] XS1_PORT_1K 1 0 ' +
                                '-port tile[0] XS1_PORT_1P 1 0 -port tile[0] XS1_PORT_1L 1 0 ' +
                                '-port tile[1] XS1_PORT_1M 1 0 -port tile[0] XS1_PORT_1F 1 0'])

def runtest():
    runtest_one_config('simulation_i2s_2in_2out_48khz')
    runtest_one_config('simulation_i2s_2in_2out_192khz')
    runtest_one_config('simulation_i2s_8in_8out_48khz')
    runtest_one_config('simulation_i2s_8in_8out_192khz')
    runtest_one_config('simulation_tdm_8in_8out_48khz')

