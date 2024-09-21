from typing import Any, overload
from math import floor

import numpy as np


class MonoChannel:
    audio: np.ndarray
    sampling_frequency: int
    def __init__(self, audio: np.ndarray, sampling_frequency: int) -> None:
        self.audio = self._check_audio(audio)
        self.sampling_frequency = sampling_frequency

    def _check_audio(self, audio: np.ndarray) -> np.ndarray:
        if not isinstance(audio, np.ndarray):
            raise TypeError('audio is not a numpy array.')
        message_1 = f'audio data shape {audio.shape} '
        message_2 = 'cannot be interpreted as a mono channel sound.'
        message = ''.join((message_1, message_2))
        shape = audio.shape
        if len(shape) > 2:
            raise ValueError(message)
        if len(shape) == 2:
            if shape[0] != 1 and shape[1] != 1:
                raise ValueError(message)
        return audio.reshape(-1)

    def __repr__(self) -> str:
        sampling_text = f'Sampling Frequency: {self.sampling_frequency} Hz'
        audio_text = f'Audio Array: {self.audio}'
        return '; '.join((sampling_text, audio_text))

    @overload
    def __getitem__(self, key: slice) -> np.ndarray:
        pass
    @overload
    def __getitem__(self, key: int) -> np.integer:
        pass
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.audio[key.start:key.stop:key.step]
        else:
            return self.audio[key]

    def __add__(self, other: 'MonoChannel') -> 'MonoChannel':
        try:
            if not isinstance(other, MonoChannel):
                raise TypeError()
            if self.sampling_frequency != other.sampling_frequency:
                message_21 = 'cannot add two audios with '
                message_22 = 'different sampling frequencies.'
                message = ''.join((message_21, message_22))
                raise ValueError(message)
            full_audio = np.concatenate((self.audio, other.audio))
            return MonoChannel(full_audio, self.sampling_frequency)
        except TypeError:
            return other + self

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MonoChannel):
            return False
        equal_audio = np.all(self.audio == other.audio)
        equal_frequency = self.sampling_frequency == other.sampling_frequency
        return equal_audio and equal_frequency

    def time_frame(self, start: float, stop: float = None) -> 'MonoChannel':
        start_index = floor(start*self.sampling_frequency)
        if stop == None or stop >= self.audio.size/self.sampling_frequency:
            stop_index = None
        else:
            stop_index = floor(stop*self.sampling_frequency)
        time_slice = slice(start_index, stop_index)
        return MonoChannel(self[time_slice], self.sampling_frequency)


def test() -> None:
    from scipy.io import wavfile

    sampling_frequency, audio = wavfile.read(r'audios/a1_com_ruido.wav', 'r')
    channel_1 = MonoChannel(audio[:, 1], sampling_frequency)
    channel_2 = MonoChannel(audio[:, 1], sampling_frequency)
    #print(channel+1)
    print(channel_1.audio.size/channel_1.sampling_frequency)
    print(channel_1.time_frame(1, 2).audio.size)
    print(channel_1 == channel_2)


if __name__ == '__main__':
    test()
