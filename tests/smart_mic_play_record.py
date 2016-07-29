#!/usr/bin/env python
import argparse
import os.path
from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import random
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

    def out_stream_callback(in_data, frame_count, time_info, status):
        data = wav_to_play.readframes(frame_count)
        return (data, pyaudio.paContinue)

    out_stream = p.open(format=FORMAT, channels=PLAYING_CHANNELS, rate=wav_to_play.getframerate(), input=False, output=True, frames_per_buffer=CHUNK_SIZE, stream_callback=out_stream_callback)

    data_all = array('h')

    chunks = int(((wav_to_play.getnframes() * sample_rate) / wav_to_play.getframerate()) / CHUNK_SIZE)

    out_stream.start_stream()
    for i in range(chunks):
        # little endian, signed short
        data_chunk = array('h', in_stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)

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
        plt.ylim([-120, 10] )
        plt.xlim([0, 24000] )
        plt.savefig(os.path.join(test_dir_path, 'plot_' + output_file_name +'.jpg'), format='jpg', dpi=400)

    return

def play_wav(test_dir_path, output_file_name, played_wav, analysis_type, sample_rate):
    sample_width, data = play_and_record(played_wav, sample_rate)

    ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_file_name = output_file_name + '_' + str(ts)

    analyse_voice(data, sample_rate)

    output_file_name = output_file_name + '.wav'
    mic_data_path = os.path.join(test_dir_path, output_file_name)

    data = pack('<' + ('h' * len(data)), *data)
    wave_file = wave.open(mic_data_path, 'wb')
    wave_file.setnchannels(RECORDING_CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(sample_rate)
    wave_file.writeframes(data)
    wave_file.close()

def generate_sine(test_dir_path, output_file_name, played_wav, analysis_type, input_sample_rate):

    output_sample_rate = 48000

    #generate sine wav called played_wav
    length_in_seconds = 30
    length_in_samples = length_in_seconds * output_sample_rate
    sine_data = []
    start_freq = 20
    end_freq = output_sample_rate/2
    theta = 0
    omega = 2.0*np.pi*end_freq/output_sample_rate
    delta_omega_per_sample =  2.0*np.pi*(end_freq - start_freq)/(length_in_samples*output_sample_rate)
    for i in range(length_in_samples):
        sample = int(np.sin(theta)*(1<<15)-1)
        sine_data.append(sample)
        theta += omega
        omega -= delta_omega_per_sample

    sine_data = np.array(sine_data, dtype=np.int16)
    sine_data = pack('<' + ('h' * len(sine_data)), *sine_data)
    sine_wave_file = wave.open(played_wav, 'wb')
    sine_wave_file.setnchannels(1)
    sine_wave_file.setsampwidth(2)
    sine_wave_file.setframerate(output_sample_rate)
    sine_wave_file.writeframes(sine_data)
    sine_wave_file.close()

    sample_width, data = play_and_record(played_wav, input_sample_rate)

    ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_file_name = output_file_name + '_' + str(ts)

    analyse_sine(data, sample_rate, test_dir_path, output_file_name)

    output_file_name = output_file_name + '.wav'
    mic_data_path = os.path.join(test_dir_path, output_file_name)

    data = pack('<' + ('h' * len(data)), *data)
    wave_file = wave.open(mic_data_path, 'wb')
    wave_file.setnchannels(RECORDING_CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(input_sample_rate)
    wave_file.writeframes(data)
    wave_file.close()
    
def generate_noise(test_dir_path, output_file_name, played_wav, analysis_type, input_sample_rate):

    output_sample_rate = 48000

    #generate sine wav called played_wav
    length_in_seconds = 30
    length_in_samples = length_in_seconds * output_sample_rate
    noise_data = []
    
    for i in range(length_in_samples):
        noise_data.append(int(random.random()*(1<<15)-1))

    noise_data = np.array(noise_data, dtype=np.int16)
    noise_data = pack('<' + ('h' * len(noise_data)), *noise_data)
    noise_file = wave.open(played_wav, 'wb')
    noise_file.setnchannels(1)
    noise_file.setsampwidth(2)
    noise_file.setframerate(output_sample_rate)
    noise_file.writeframes(noise_data)
    noise_file.close()

    sample_width, data = play_and_record(played_wav, input_sample_rate)

    ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_file_name = output_file_name + '_' + str(ts)

    analyse_sine(data, sample_rate, test_dir_path, output_file_name)

    output_file_name = output_file_name + '.wav'
    mic_data_path = os.path.join(test_dir_path, output_file_name)

    data = pack('<' + ('h' * len(data)), *data)
    wave_file = wave.open(mic_data_path, 'wb')
    wave_file.setnchannels(RECORDING_CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(input_sample_rate)
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
                           choices=['voice', 'sine', 'noise'],
                           default='voice',
                           help ='The type of analysis')
    args = argparser.parse_args()

    sample_rate = int(args.sample_rate)

    if str(args.analysis_type) == 'voice':
        play_wav(args.test_dir_path, args.output_file_name,
                   args.playback_file, args.analysis_type, sample_rate)
    elif str(args.analysis_type) == 'sine':
        generate_sine(args.test_dir_path, args.output_file_name,
                   args.playback_file, args.analysis_type, sample_rate)
    elif str(args.analysis_type) == 'noise':
        generate_noise(args.test_dir_path, args.output_file_name,
                   args.playback_file, args.analysis_type, sample_rate)
    else:
        print "error"

