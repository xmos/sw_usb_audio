#!/usr/bin/env python
import argparse
import subprocess
import os.path


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description = "Smart mic generate/record script")
    argparser.add_argument('generator_mode',
                           choices=['frequency-sweep', 'noise'],
                           help ='type of signal to generate',
                           metavar='generator-mode')
    argparser.add_argument('output_directory',
                           help='directory where generated file will be placed',
                           metavar='output-directory')
    argparser.add_argument('duration',
                           default=30,
                           type=int,
                           help='length in seconds for the generated sound')
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

    # Generate required test files
    gen_freq = 48000
    gen_name = os.path.join(script_location,
                            'generated_%s_%dHz_%ds.wav' % (args.generator_mode,
                                                           gen_freq,
                                                           args.duration))
    subprocess.check_call(['python', os.path.join(script_location, 'generate_wav.py'),
                           '--output-directory', args.output_directory,
                           '--output-filename', gen_name,
                           '--duration', str(args.duration),
                           str(gen_freq), args.generator_mode])

    # Play and record
    subprocess.check_call(['python', os.path.join(script_location, 'play_record_wav.py'),
                           '--playback-device-name', 'Built-in Output',
                           '--recording-filename', args.recording_filename,
                           '--recording-device-name', 'XMOS Microphone Array UAC',
                           '--recording-sample-rate', str(args.recording_sample_rate),
                           '--recording-sample-width', '2',
                           '--recording-channel-count', '1',
                           gen_name])

    # Analyse recorded file
    subprocess.check_call(['python', os.path.join(script_location, 'analyse_wav.py'),
                           '--output-directory', args.output_directory,
                           args.recording_filename,
                           'sine'])
