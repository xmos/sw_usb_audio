#!/usr/bin/env python
import argparse
import os.path
import numpy as np
import matplotlib.pyplot as plt
from array import array
from scipy.io import wavfile


def read_wav(filename):
    audio_data = []
    sample_rate, chan_tuples = wavfile.read(filename)
    try:
        channel_count = len(chan_tuples[0])
        for channel in range(channel_count):
            audio_data.append(array('h', chan_tuples[:,channel]))
    except TypeError:
        # If chan_tuples isn't an array of arrays then it must be a mono WAV
        channel_count = 1
        audio_data.append(array('h', chan_tuples))

    return audio_data, channel_count, sample_rate


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def plot_fft(filename, max_response, sample_rate, window_length):
    plt.clf()
    x=[]
    plt.xlabel('Frequency')
    plt.ylabel('Magnitude')
    plt.grid(True)
    for i in range(len(max_response)):
        x.append(int(sample_rate*i/window_length))
    plt.plot(x, 20*np.log10(smooth(max_response, 5)/(window_length**2)))
    plt.ylim([-120, 10])
    plt.xlim([0, 24000])
    plt.savefig(filename, format='pdf', dpi=400)


def analyse_sine(audio_data, channel_count, sample_rate):
    window_length = 4096
    windowing_function = np.hanning(window_length)

    for chan in range(channel_count):
        max_response = [0.0]*(window_length/2 + 1)
        channel_data = audio_data[chan]

        for frame_start in range(0, len(channel_data)-window_length, window_length/16):
            wav_frame = channel_data[frame_start:frame_start + window_length]

            frame = np.array(wav_frame, dtype=float)

            for i in range(window_length):
                frame[i] *= windowing_function[i]

            frame_frequencies = np.fft.rfft(frame)

            for i in range(len(frame_frequencies)):
                max_response[i] = max(max_response[i], abs(frame_frequencies[i]))

        return max_response, window_length


def analyse_voice(audio_data, channel_count, sample_rate):
    HPF_CUT_OFF_HZ = 50.0
    results = []

    for chan in range(channel_count):
        channel_data = audio_data[chan]
        channel_frequencies = np.fft.fft(channel_data)
        start_bin = int(HPF_CUT_OFF_HZ * float(len(channel_frequencies)) / float(sample_rate))
        energy = 0.0
        for b in range(start_bin, len(channel_frequencies)):
            energy += abs(channel_frequencies[b])
        results.append(str(chan) +" " + str(energy))

    return results


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='XMOS WAV analysis script')
    argparser.add_argument('input_filename',
                           help='filename of the WAV to analyse',
                           metavar='input-filename')
    argparser.add_argument('analysis_mode',
                           choices=['sine', 'voice'],
                           help='type of content to analyse',
                           metavar='analysis-mode')
    argparser.add_argument('--output-directory',
                           default='.',
                           help='directory where generated file will be placed')
    argparser.add_argument('--output-filename',
                           help='filename to use for the generated FFT plot')

    args = argparser.parse_args()

    # Setup default values which cannot be handled by argparser as required
    if args.output_filename is None:
        # Use the input filename, without path or file extension
        args.output_filename = 'plot_%s.pdf' % args.input_filename.split(os.sep)[-1].rstrip('.wav')
    output_path = os.path.join(args.output_directory, args.output_filename)

    audio_data, channel_count, sample_rate = read_wav(args.input_filename)

    if args.analysis_mode == 'sine':
        max_response, window_length = analyse_sine(audio_data, channel_count, sample_rate)
        plot_fft(output_path, max_response, sample_rate, window_length)
    elif args.analysis_mode == 'voice':
        print analyse_voice(audio_data, channel_count, sample_rate)
    else:
        print 'Error: failed to select an analysis mode correctly'
        exit(1)
