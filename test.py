from pathlib import Path

import numpy as np
from scipy.io import wavfile

FILEPATH = Path(r'audios/see-you-later-203103.wav')

from mono import MonoChannel
from stereo import StereoSound
from filters.equalizers import BASS_BOOST


def main():
    mono_channel = MonoChannel(np.array([1, 2, 3, 4, 5, 6]), 44100)
    left = MonoChannel(np.array([1, 2, 3, 4, 5]), 44100)
    right = MonoChannel(np.array([4, 5, 6, 7, 8]), 44100)
    audio = StereoSound((left, right))
    print(audio//mono_channel == mono_channel//audio)

    #audio = StereoSound((left, right))

    #monotest = MonoChannel(5, 44100, is_length=False)
    #print(monotest, monotest.length)


if __name__ == '__main__':
    main()
