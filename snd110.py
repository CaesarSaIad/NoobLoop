# snd110.py -- audio generation and IO

import wave
from math import *
from array import array
from struct import pack, unpack_from

ARATE = 44100
MAX_AMP = 0x7FFF

def sine_tone(freq, dur, amp):
    sine = [0.0] * int(dur * ARATE)
    for i in range(len(sine)):
        sine[i] = amp * sin(i * 2 * pi * freq / ARATE)
    return envelope(sine, 0.1, 0.2)

def samples_to_shorts(sound):
    data = bytearray()
    for s in sound:
        if abs(s) > 1:
            s = s / abs(s)
        data += pack('h', int(MAX_AMP * s))
    return data

def write_wave(name, sound):
    wf = wave.open(name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(ARATE)
    wf.writeframes(samples_to_shorts(sound))
    #wf.writeframes(samples_to_shorts(sound))
    wf.close()

def envelope(sound, attack, decay):
    # attack is the duration of the onset
    # decay is the duration of the ending
    attack = int(attack * 44100) # convert to samples
    decay = int(decay * 44100)
    if attack + decay > len(sound):
        attack = len(sound) // 2
        decay = attack
    for i in range(attack):
        sound[i] = sound[i] * i / attack
    last = len(sound) - 1
    for i in range(decay):
        sound[last - i] = sound[last - i] * i / decay
    return sound


def read_wave(name):
    wf = wave.open(name, 'rb')
    size = wf.getnframes()
    chans = wf.getnchannels()
    data = wf.readframes(size)
    samples = []
    skip = 2 * chans # the frame size
    for i in range(size): # read first sample of each frame
        samples.append(
            unpack_from('h', data, offset = i * skip)[0] / MAX_AMP)
    return samples

