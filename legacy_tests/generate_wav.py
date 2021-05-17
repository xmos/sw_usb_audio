#!/usr/bin/env python
import argparse
import os.path
import wave
import random
import numpy as np
from struct import pack


def write_wav_file(filename, sample_rate, data):
    data = np.array(data, dtype=np.int16)
    data = pack('<' + ('h' * len(data)), *data)
    wav_file = wave.open(filename, 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(data)
    wav_file.close()


def generate_frequency_sweep(sample_rate, duration, min_freq, max_freq):
    length_in_samples = duration * sample_rate
    sine_data = []
    theta = 0
    omega = 2.0*np.pi*max_freq/sample_rate
    delta_omega_per_sample =  2.0*np.pi*(max_freq - min_freq)/(length_in_samples*sample_rate)

    for i in range(length_in_samples):
        sample = int(np.sin(theta)*(1<<15)-1)
        sine_data.append(sample)
        theta += omega
        omega -= delta_omega_per_sample

    return sine_data


def generate_noise(sample_rate, duration):
    length_in_samples = duration * sample_rate
    noise_data = []

    for i in range(length_in_samples):
        noise_data.append(int(random.uniform(-1,1)*(1<<15)-1))

    return noise_data


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='XMOS WAV generator script',
                                        epilog='Produces 16bit mono files only!')

    # Output file options
    argparser.add_argument('--output-directory',
                           default='.',
                           help='directory where generated file will be placed')
    argparser.add_argument('--output-filename',
                           help='filename to use for the generated file')
    argparser.add_argument('--duration',
                           default=30,
                           type=int,
                           help='length in seconds for the generated sound')
    argparser.add_argument('sample_rate',
                           type=int,
                           help='sample rate in Hz for the generated file')

    # Signal generator options
    gen_argparser = argparser.add_subparsers(title='generator arguments',
                                             help='type of content to generate')

    freq_sweep_argparser = gen_argparser.add_parser('frequency-sweep',
                                                    help='generate a frequency sweep')
    # Use the subcommand name to identify which subparser fires
    freq_sweep_argparser.set_defaults(gen_mode=freq_sweep_argparser.prog.split()[-1])
    freq_sweep_argparser.add_argument('--min-freq',
                                      default=0,
                                      help='minimum frequency in sweep, in Hz')
    freq_sweep_argparser.add_argument('--max-freq',
                                      help='maximum frequency in sweep, in Hz')

    noise_argparser = gen_argparser.add_parser('noise',
                                               help='generate noise')
    # Use the subcommand name to identify which subparser fires
    noise_argparser.set_defaults(gen_mode=noise_argparser.prog.split()[-1])

    args = argparser.parse_args()

    # Setup default values which cannot be handled by argparser as required
    if args.output_filename is None:
        args.output_filename = 'generated_%s_%dHz_%ds.wav' % (args.gen_mode,
                                                              args.sample_rate,
                                                              args.duration)
    output_path = os.path.join(args.output_directory, args.output_filename)

    # Generate the requested type of content
    if args.gen_mode == 'frequency-sweep':
        if args.max_freq is None:
            args.max_freq = args.sample_rate/2

        audio_data = generate_frequency_sweep(args.sample_rate, args.duration,
                                              args.min_freq, args.max_freq)
    elif args.gen_mode == 'noise':
        audio_data = generate_noise(args.sample_rate, args.duration)
    else:
        print 'Error: failed to select a generator mode correctly'
        exit(1)

    # Create the WAV file
    write_wav_file(output_path, args.sample_rate, audio_data)
