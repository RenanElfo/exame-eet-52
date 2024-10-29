from pathlib import Path
from typing import Any, Union, overload, NoReturn

import numpy as np
import matplotlib.pyplot as plt

from filters.equalizer import Equalizer
import stereo as s

Number = Union[float, int, np.integer, np.floating]


class MonoChannel:
    audio: np.ndarray
    sampling_frequency: Number

    @overload
    def __init__(self, audio: np.ndarray, sampling_frequency: Number, *,
                 is_length: bool) -> None:
        pass
    @overload
    def __init__(self, audio: Number, sampling_frequency: Number, *,
                 is_length: bool) -> None:
        pass
    def __init__(self, audio, sampling_frequency, *, is_length = True):
        if isinstance(audio, Number):
            lenght = audio
            size = lenght*sampling_frequency if is_length else audio
            audio = np.zeros(size)
        elif not isinstance(audio, np.ndarray):
            message_1 = 'must pass audio as numpy array '
            message_2 = 'or lenght as a number.'
            raise TypeError(''.join((message_1, message_2)))
        if sampling_frequency <= 0:
            return ValueError('sampling frequency must be a positive number.')
        self.audio = self._validate_audio(audio)
        self.sampling_frequency = sampling_frequency

    def _validate_audio(self, audio: np.ndarray) -> np.ndarray:
        if not isinstance(audio, np.ndarray):
            raise TypeError('audio is not a numpy array.')
        shape = np.array(audio.shape)
        if np.sum(shape > 1) > 1 and not np.all(shape == 1):
            message_1 = f'audio data shape {audio.shape} '
            message_2 = 'cannot be interpreted as a mono channel sound.'
            message = ''.join((message_1, message_2))
            raise ValueError(message)
        return audio.reshape(-1)

    @property
    def size(self) -> int:
        return int(self.audio.size)

    @property
    def length(self) -> float:
        return self.size/self.sampling_frequency

    @property
    def time(self) -> float:
        return np.linspace(0, self.length, self.size)

    def __repr__(self) -> str:
        freq_text = f'Sampling Frequency: {self.sampling_frequency:.0f} Hz'
        audio_text = f'Audio Array: {self.audio}'
        return '; '.join((freq_text, audio_text))

    @overload
    def __getitem__(self, key: slice) -> 'MonoChannel':
        pass
    @overload
    def __getitem__(self, key: int) -> np.integer:
        pass
    def __getitem__(self, key):
        if isinstance(key, slice):
            audio_slice = self.audio[key.start:key.stop:key.step]
            return MonoChannel(audio_slice, self.sampling_frequency)
        else:
            return self.audio[key]

    @overload
    def __sub__(self, other: 'MonoChannel') -> 'MonoChannel':
        pass
    @overload
    def __sub__(self, other: 's.StereoSound') -> 's.StereoSound':
        pass
    def __sub__(self, other):
        if not isinstance(other, (s.StereoSound, MonoChannel)):
            message = f"can't merge MonoChannel and {type(other).__name__}."
            raise TypeError(message)
        if self.sampling_frequency != other.sampling_frequency:
            message_21 = 'cannot merge two audios with '
            message_22 = 'different sampling frequencies.'
            message = ''.join((message_21, message_22))
            raise ValueError(message)
        if isinstance(other, s.StereoSound):
            left_channel = MonoChannel(
                np.concatenate((self.audio, other.left_channel.audio)),
                self.sampling_frequency
            )
            right_channel = MonoChannel(
                np.concatenate((self.audio, other.right_channel.audio)),
                self.sampling_frequency
            )
            return s.StereoSound((left_channel, right_channel))
        full_audio = np.concatenate((self.audio, other.audio))
        return MonoChannel(full_audio, self.sampling_frequency)

    @overload
    def __floordiv__(self, other: 'MonoChannel') -> 'MonoChannel':
        pass
    @overload
    def __floordiv__(self, other: 's.StereoSound') -> 's.StereoSound':
        pass
    def __floordiv__(self, other):
        if not isinstance(other, (s.StereoSound, MonoChannel)):
            message_11 = f"can't overlap MonoChannel and "
            message_12 = f'{type(other).__name__}'
            raise TypeError(''.join((message_11, message_12)))
        if self.sampling_frequency != other.sampling_frequency:
            message_21 = 'cannot overlap two audios with '
            message_22 = 'different sampling frequencies.'
            message = ''.join((message_21, message_22))
        bigger_size = max(self.size, other.size)
        padded_self = self.add_padding(
            bigger_size - self.size, is_right_padding=True
        )
        padded_other = other.add_padding(
            bigger_size - other.size, is_right_padding=True
        )
        if isinstance(other, s.StereoSound):
            left_channel = MonoChannel(
                padded_self.audio + padded_other.left_channel.audio,
                self.sampling_frequency
            )
            right_channel = MonoChannel(
                padded_self.audio + padded_other.right_channel.audio,
                self.sampling_frequency
            )
            return s.StereoSound((left_channel, right_channel))
        overlapped_audio = padded_self.audio + padded_other.audio
        return MonoChannel(overlapped_audio, self.sampling_frequency)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MonoChannel):
            return False
        equal_audio = np.all(self.audio == other.audio)
        equal_frequency = self.sampling_frequency == other.sampling_frequency
        return equal_audio and equal_frequency

    def add_padding(
            self, ammount: int,
            is_right_padding: bool = False,
            is_lenght = False) -> 'MonoChannel':
        padding_audio = MonoChannel(
            ammount, self.sampling_frequency, is_length=is_lenght
        )
        if is_right_padding:
            return self - padding_audio
        return padding_audio - self

    def to_stereo(self) -> 's.StereoSound':
        return s.StereoSound((self, self))

    def plot_audio(self, start: float = 0, stop: float = None) -> None:
        frame = self.time_frame(start, stop)
        plt.figure()
        plt.plot(frame.time, frame.audio)
        plt.show()

    def time_frame(self, start: float, stop: float = None) -> 'MonoChannel':
        start_index = int(np.floor(start*self.sampling_frequency))
        if stop == None or stop >= self.length:
            stop_index = None
        else:
            stop_index = int(np.floor(stop*self.sampling_frequency))
        time_slice = slice(start_index, stop_index)
        return self[time_slice]

    def filter_audio(self, filter: Equalizer) -> 'MonoChannel':
        nyquist = self.sampling_frequency/2
        frequencies = filter.frequencies
        if nyquist <= frequencies[-1]:
            high_frequencies = high_frequencies[frequencies > nyquist]
            frequencies = frequencies[frequencies <= nyquist]
            high_freq_gain = gain.copy()
            high_freq_gain = high_freq_gain[frequencies > nyquist]
            gain = filter.gain[frequencies <= nyquist]
        if nyquist not in frequencies:
            frequencies = np.append(frequencies, nyquist)
