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
import datetime

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
RATE = 16000
RECORDING_CHANNELS = 1
PLAYING_CHANNELS = 1

HPF_CUT_OFF_HZ = 50.0

def play_and_record(played_wav):

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

    out_stream = p.open(format=FORMAT, channels=PLAYING_CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)
    in_stream = p.open(format=FORMAT, channels=RECORDING_CHANNELS, rate=RATE, input=True, output=False, frames_per_buffer=CHUNK_SIZE, input_device_index = mic_array_index)

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


def analyse(data):
    #do a real fft
    for chan in range(RECORDING_CHANNELS):
        channel_data = data[chan:-1:RECORDING_CHANNELS]
        channel_frequencies = np.fft.fft(channel_data)
        start_bin = int(HPF_CUT_OFF_HZ * float(len(channel_frequencies)) / float(RATE))
        energy = 0.0
        for b in range(start_bin, len(channel_frequencies)):
            energy += abs(channel_frequencies[b])
        print str(chan) +" " + str(energy)
    return

def record_to_file(test_dir_path, output_file_name, played_wav):
    sample_width, data = play_and_record(played_wav)

    analyse(data)

    ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    output_file_name = output_file_name + str(ts) + '.wav'
    mic_data_path = os.path.join(test_dir_path, output_file_name)

    data = pack('<' + ('h' * len(data)), *data)
    wave_file = wave.open(mic_data_path, 'wb')
    wave_file.setnchannels(RECORDING_CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(RATE)
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
    args = argparser.parse_args()

    record_to_file(args.test_dir_path, args.output_file_name, args.playback_file)
