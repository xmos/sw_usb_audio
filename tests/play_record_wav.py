#!/usr/bin/env python
import argparse
import os.path
import pyaudio
import wave
from array import array
from sys import byteorder
from datetime import datetime
from generate_wav import write_wav_file


def play_and_record(pb_filename, pb_dev_name,
                    rec_dev_name, rec_sample_rate, rec_sample_width, rec_channel_count):
    CHUNK_SIZE = 1024

    audio_manager = pyaudio.PyAudio()
    device_count = audio_manager.get_device_count()
    print "There are " + str(device_count) + " devices"

    # Look for the requested playback device
    pb_dev_index = -1
    pb_dev_found = False
    for i in range(device_count):
        if pb_dev_name in audio_manager.get_device_info_by_index(i)['name']:
            print "Selecting device '" + audio_manager.get_device_info_by_index(i)['name'] + "' for playback"
            pb_dev_index = i
            pb_dev_found = True
            break

    if pb_dev_found == False:
        print "Totally ruined: Playback device not found"
        return

    # Look for the requested recording device
    rec_dev_index = -1
    rec_dev_found = False
    for i in range(device_count):
        if rec_dev_name in audio_manager.get_device_info_by_index(i)['name']:
            print "Selecting device '" + audio_manager.get_device_info_by_index(i)['name'] + "' for recording"
            rec_dev_index = i
            rec_dev_found = True
            break

    if rec_dev_found == False:
        print "Totally ruined: Recording device not found"
        return

    wav_to_play = wave.open(pb_filename, 'rb')

    def out_stream_callback(in_data, frame_count, time_info, status):
        data = wav_to_play.readframes(frame_count)
        return (data, pyaudio.paContinue)

    out_stream = audio_manager.open(format=audio_manager.get_format_from_width(
                                        wav_to_play.getsampwidth()),
                                    channels=wav_to_play.getnchannels(),
                                    rate=wav_to_play.getframerate(),
                                    input=False, output=True,
                                    frames_per_buffer=CHUNK_SIZE,
                                    output_device_index=pb_dev_index,
                                    stream_callback=out_stream_callback)

    in_stream = audio_manager.open(format=audio_manager.get_format_from_width(rec_sample_width),
                                   channels=rec_channel_count,
                                   rate=rec_sample_rate,
                                   input=True, output=False,
                                   frames_per_buffer=CHUNK_SIZE,
                                   input_device_index=rec_dev_index)

    recorded_data = array('h')

    chunks = int(((wav_to_play.getnframes() * wav_to_play.getframerate()) / wav_to_play.getframerate()) / CHUNK_SIZE)

    out_stream.start_stream()
    for i in range(chunks):
        # little endian, signed short
        data_chunk = array('h', in_stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        recorded_data.extend(data_chunk)

    out_stream.stop_stream()
    out_stream.close()
    in_stream.stop_stream()
    in_stream.close()
    audio_manager.terminate()
    return recorded_data


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='XMOS synchronised WAV play/record script')
    argparser.add_argument('playback_filename',
                           help='filename of the WAV to play',
                           metavar='playback-filename')
    argparser.add_argument('--playback-device-name',
                           default='Built-in Output',
                           help ='name of the playback device')
    argparser.add_argument('--recording-directory',
                           default='.',
                           help='directory where recorded file will be placed')
    argparser.add_argument('--recording-filename',
                           help='filename to use for the recorded WAV')
    argparser.add_argument('--recording-device-name',
                           default='XMOS Microphone Array UAC',
                           help ='name of the recording device')
    argparser.add_argument('--recording-sample-rate',
                           default=16000,
                           type=int,
                           help ='sample rate in Hz for recording device')
    argparser.add_argument('--recording-sample-width',
                           default=2,
                           type=int,
                           help ='sample width in bytes for recording device')
    argparser.add_argument('--recording-channel-count',
                           default=1,
                           type=int,
                           help ='number of channels to use on recording device')

    args = argparser.parse_args()

    ts = datetime.now().strftime('%Y%m%d_%H-%M-%S')

    # Setup default values which cannot be handled by argparser as required
    if args.recording_filename is None:
        args.recording_filename = 'recording_%s.wav' % ts
    recording_path = os.path.join(args.recording_directory, args.recording_filename)

    # Play and record to the specified audio devices
    recorded_data = play_and_record(args.playback_filename, args.playback_device_name,
                                    args.recording_device_name, args.recording_sample_rate,
                                    args.recording_sample_width, args.recording_channel_count)

    # Save the captured date in a WAV file
    write_wav_file(recording_path, args.recording_sample_rate, recorded_data)
