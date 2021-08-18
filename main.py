# -*- coding: utf-8 -*-
import pyaudio
import wave
import termcolor as t
import numpy
from matplotlib import pyplot as plt
from sounddevice import query_hostapis

def dialog_choosing_input_device(p: pyaudio.PyAudio):
    print('Do you want to choose audio device or use default device? Print Yes, if you want to choose, else print No.')
    while True:
        inp = input()
        if inp.isalpha():
            if inp.lower() == 'yes':
                info = p.get_host_api_info_by_index(0)
                numdevices = info.get('deviceCount')
                for i in range(0, numdevices):
                    name = ''
                    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                        device_info = pyaudio.pa.get_device_info(pyaudio.pa.host_api_device_index_to_device_index(0, i))
                        name_bytes = device_info.name
                        try:

                            # THIS WAS COPIED FROM SOUNDDEVICE MODULE BECAUSE OF
                            # PROBLEMS WITH DEVICES' NAMES IN CYRILLIC-BASED WINDOWS

                            # We don't know beforehand if DirectSound and MME device names use
                            # 'utf-8' or 'mbcs' encoding.  Let's try 'utf-8' first, because it more
                            # likely raises an exception on 'mbcs' data than vice versa, see also
                            # All other host APIs use 'utf-8' anyway.

                            name = name_bytes.decode('utf-8')
                        except:
                            try:
                                name = name_bytes.decode('mbcs')
                            except:
                                print("Something bad happened with decoding your device's name. Try again...")

                        print("Input Device id ", i, " - ", name, query_hostapis(device_info.hostApi)['name'])
                while True:
                    device = input('Choose device by its number: ')
                    if device.isdigit():
                        if str(float(device)) != device:
                            if int(device) in range(0, numdevices):
                                device = int(device)
                                break
                            else:
                                print("It seems that input isn't in a list of functions. Please write correct value")
                                introduction()
                        else:
                            print("It seems that input isn't a integer. Please write correct value")
                            introduction()
                    else:
                        print("It seems that input isn't a digit. Please write correct value")
                        introduction()
                break
            elif inp.lower() == 'no':
                device = None
                break
            else:
                print("Program doesn't recognise you. Try again!")
        else:
            print("Program doesn't recognise you. Try again!")
    return device

def decode_to_multidimensional_numpy_array(array_1D, channels):
    print(len(array_1D))
    chunk = len(array_1D) / channels
    assert chunk == int(chunk)
    return numpy.reshape(array_1D, (chunk, channels))

def record_sound_to_wav():
    p = pyaudio.PyAudio()

    device = dialog_choosing_input_device(p)

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = int(input('Write count of channels: '))
    RATE = 44100
    RECORD_SECONDS = int(input('Write duration for recording (sec): '))
    WAVE_OUTPUT_FILENAME = "{}.wav".format(input('Write name for your music file: '))

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=device)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def record_sound_and_plot():
    p = pyaudio.PyAudio()

    device = dialog_choosing_input_device(p)

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = int(input('Write count of channels: '))
    RATE = 48000
    RECORD_SECONDS = int(input('Write duration for recording (sec): '))

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=device)

    print("* recording")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(numpy.fromstring(data, dtype=numpy.int16))

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    if CHANNELS == 1:
        numpydata = numpy.hstack(frames)
    else:
        numpydata = decode_to_multidimensional_numpy_array(frames, CHANNELS)

    plt.plot(numpydata)
    plt.show()

DICT_OF_FUNCTIONS = {'Record sound to .WAV': record_sound_to_wav, 'Record sound and plot': record_sound_and_plot}

def introduction():
    print('Welcome to Chords!')
    print('What you want to do? Please, choose one function from list below and write its number.')
    print('If you want to exit, write "exit"')
    for i in range(len(DICT_OF_FUNCTIONS.items())):
        print(t.colored('{}. {}'.format(str(i+1), list(DICT_OF_FUNCTIONS.items())[i][0]), 'magenta'))
    COMMAND = input()
    if COMMAND.isdigit():
        if str(float(COMMAND)) != COMMAND:
            if 0 < int(COMMAND) < (len(DICT_OF_FUNCTIONS.items()) + 1):
                print(t.colored('Function begins!', 'red'))
                DICT_OF_FUNCTIONS[list(DICT_OF_FUNCTIONS.items())[int(COMMAND)-1][0]]()
            else:
                print("It seems that input isn't in a list of functions. Please write correct value")
                introduction()
                return None
        else:
            print("It seems that input isn't a integer. Please write correct value")
            introduction()
            return None
    else:
        print("It seems that input isn't a digit. Please write correct value")
        introduction()
        return None
if __name__ == '__main__':
    introduction()
