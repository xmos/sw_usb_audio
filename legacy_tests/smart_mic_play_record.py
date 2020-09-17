#!/usr/bin/env python
import argparse
import subprocess
import os.path


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description = "Smart mic play/record script")
    argparser.add_argument('playback_filename',
                           help='filename of the WAV to play',
                           metavar='playback-filename')
    # analyse_wav.py does not write results of 'voice' analysis to file currently
    # argparser.add_argument('output_directory',
    #                        help='directory where generated file will be placed',
    #                        metavar='output-directory')
    argparser.add_argument('recording_filename',
                           help='filename to use for the recorded WAV',
                           metavar='recording-filename')
    argparser.add_argument('recording_sample_rate',
                           type=int,
                           help ='sample rate in Hz for recording device',
                           metavar='recording-sample-rate')

    args = argparser.parse_args()

    # Avoid issues when called by xmostest from a different location
    script_location = os.path.dirname(os.path.realpath(__file__))

    # Play and record
    subprocess.check_call(['python', os.path.join(script_location, 'play_record_wav.py'),
                           '--playback-device-name', 'Built-in Output',
                           '--recording-filename', args.recording_filename,
                           '--recording-device-name', 'XMOS Microphone Array UAC',
                           '--recording-sample-rate', str(args.recording_sample_rate),
                           '--recording-sample-width', '2',
                           '--recording-channel-count', '1',
                           args.playback_filename])

    # Analyse recorded file
    subprocess.check_call(['python', os.path.join(script_location, 'analyse_wav.py'),
                           # '--output-directory', args.output_directory,
                           args.recording_filename,
                           'voice'])
