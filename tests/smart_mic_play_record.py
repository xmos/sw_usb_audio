#!/usr/bin/env python
import argparse
import os.path
from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
RECORDING_CHANNELS = 1
PLAYING_CHANNELS = 1

HPF_CUT_OFF_HZ = 50.0

def play_and_record(played_wav, sample_rate):

    wav_to_play = wave.open(played_wav, 'rb')

    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print "There are " + str(device_count) + " devices"

    mic_array_index = -1
    mic_array_found = False
    for i in range(device_count):
       if 'XMOS Microphone Array UAC' in p.get_device_info_by_index(i)['name']:
          print "Selecting device: " + p.get_device_info_by_index(i)['name']
          mic_array_index = i
          mic_array_found = True
          break

    if mic_array_found == False:
       print "Totally ruined: Mic array not found"
       return

    in_stream = p.open(format=FORMAT, channels=RECORDING_CHANNELS, rate=sample_rate, input=True, output=False, frames_per_buffer=CHUNK_SIZE, input_device_index = mic_array_index)
    out_stream = p.open(format=FORMAT, channels=PLAYING_CHANNELS, rate=sample_rate, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

    data_all = array('h')

    chunks = int(wav_to_play.getnframes()/ CHUNK_SIZE)

    for i in range(chunks):
        # little endian, signed short
        data_chunk = array('h', out_stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)

        out_data = wav_to_play.readframes(CHUNK_SIZE)
        out_stream.write(out_data, CHUNK_SIZE)

    sample_width = p.get_sample_size(FORMAT)
    out_stream.stop_stream()
    out_stream.close()
    in_stream.stop_stream()
    in_stream.close()
    p.terminate()
    return sample_width, data_all


def analyse_voice(data, sample_rate):
    #do a real fft
    for chan in range(RECORDING_CHANNELS):
        channel_data = data[chan:-1:RECORDING_CHANNELS]
        channel_frequencies = np.fft.fft(channel_data)
        start_bin = int(HPF_CUT_OFF_HZ * float(len(channel_frequencies)) / float(sample_rate))
        energy = 0.0
        for b in range(start_bin, len(channel_frequencies)):
            energy += abs(channel_frequencies[b])
        print str(chan) +" " + str(energy)
    return

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def analyse_sine(data, sample_rate, test_dir_path, output_file_name):
    #do a real fft

    window_length = 4096
    windowing_function = np.hanning(window_length)

    for chan in range(RECORDING_CHANNELS):
        max_response = [0.0]*(window_length/2 + 1)
        channel_data = data[chan:-1:RECORDING_CHANNELS]

        for frame_start in range(0, len(channel_data)-window_length, window_length/2):
            wav_frame = channel_data[frame_start:frame_start + window_length]

            frame = np.array(wav_frame, dtype=float)

            for i in range(window_length):
                frame[i] *= windowing_function[i]

            frame_frequencies = np.fft.rfft(frame)

            for i in range(len(frame_frequencies)):
                max_response[i] = max(max_response[i], abs(frame_frequencies[i]))

        plt.clf()
        x=[]
        plt.xlabel('Frequency')
        plt.ylabel('Magnitude')
        plt.grid(True)
        for i in range(len(max_response)):
           x.append(int(sample_rate*i/window_length))
        plt.plot(x, 20*np.log10(smooth(max_response, 5)/(window_length**2)))
        plt.savefig(os.path.join(test_dir_path, 'plot_' + output_file_name +'.jpg'), format='jpg', dpi=400)

    return

def record_to_file(test_dir_path, output_file_name, played_wav, analysis_type, sample_rate):
    sample_width, data = play_and_record(played_wav, sample_rate)

    ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_file_name = output_file_name + '_' + str(ts)

    if analysis_type is 'voice':
        analyse_voice(data, sample_rate)
    else:
        analyse_sine(data, sample_rate, test_dir_path, output_file_name)

    output_file_name = output_file_name + '.wav'
    mic_data_path = os.path.join(test_dir_path, output_file_name)

    data = pack('<' + ('h' * len(data)), *data)
    wave_file = wave.open(mic_data_path, 'wb')
    wave_file.setnchannels(RECORDING_CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(sample_rate)
    wave_file.writeframes(data)
    wave_file.close()

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description = "Smart mic play/record script")
    argparser.add_argument('--test_dir_path',
                           metavar='.',
                           default='.',
                           help ='Path to where the recording output should go')
    argparser.add_argument('--output_file_name',
                           metavar='recording',
                           default='recording',
                           help ='The file name to capture mic data to')
    argparser.add_argument('--playback_file',
                           metavar=os.path.join('test_audio','audio_book.wav'),
                           default=os.path.join('test_audio','oliver_twist.wav'),
                           help ='The file to play from')
    argparser.add_argument('--sample_rate',
                           metavar='16000',
                           default='16000',
                           help ='The play/record sample rate in Hz')
    argparser.add_argument('--analysis_type',
                           choices=['voice', 'sine'],
                           default='voice',
                           help ='The type of analysis')
    args = argparser.parse_args()

    sample_rate = int(args.sample_rate)

    record_to_file(args.test_dir_path, args.output_file_name,
                   args.playback_file, args.analysis_type, sample_rate)
