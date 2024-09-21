from pathlib import Path
from typing import Any, Union, Tuple, overload
from math import floor

import numpy as np
from scipy.io import wavfile

from mono import MonoChannel

Sound = Union['StereoSound', MonoChannel]


class StereoSound:
    left_channel: MonoChannel
    right_channel: MonoChannel
    sampling_frequency: int
    @overload
    def __init__(self, audio: Path) -> None:
        pass
    @overload
    def __init__(self, audio: Tuple[MonoChannel, MonoChannel]) -> None:
        pass
    def __init__(self, audio):
        if isinstance(audio, Path):
            sampling_frequency, data = wavfile.read(audio, 'r')
            self.left_channel = MonoChannel(data[:, 0], sampling_frequency)
            self.right_channel = MonoChannel(data[:, 1], sampling_frequency)
            self.sampling_frequency = sampling_frequency
        elif not isinstance(audio, tuple):
            message_11 = 'cannot instantiate class with parameters provided. '
            message_12 = 'Can only take path to .wav file or tuple containing'
            message_13 = ' left and right channels as MonoChannel instances.'
            raise TypeError(''.join((message_11, message_12, message_13)))
        else:
            if not (isinstance(audio[0], MonoChannel)
                    and isinstance(audio[1], MonoChannel)) or len(audio) != 2:
                message_21 = 'tuple given must contain exactly two '
                message_22 = 'instances of MonoChannel class.'
                raise ValueError(''.join((message_21, message_22)))
            left_channel, right_channel = audio[0], audio[1]
            self.sampling_frequency = left_channel.sampling_frequency
            if self.sampling_frequency != right_channel.sampling_frequency:
                message_31 = 'channels cannot have different '
                message_32 = 'sampling frequencies.'
                raise ValueError(''.join((message_31, message_32)))
            self.left_channel = left_channel
            self.right_channel = right_channel
    
    def __repr__(self) -> str:
        sampling_text = f'Sampling Frequency: {self.sampling_frequency} Hz'
        left_text = f'Left Channel Data: {self.left_channel.audio}'
        right_text = f'Right Channel Data: {self.right_channel.audio}'
        return '; '.join((sampling_text, left_text, right_text))

    def __add__(self, other: Sound) -> 'StereoSound':
        if not isinstance(other, (StereoSound, MonoChannel)):
            message_11 = f"unsupported operand type(s) for +: '{type(self)} '"
            message_12 = f"and '{type(other)}'."
            raise TypeError(''.join((message_11, message_12)))
        if self.sampling_frequency != other.sampling_frequency:
            message_21 = 'cannot add two audios with '
            message_22 = 'different sampling frequencies.'
            message = ''.join((message_21, message_22))
            raise ValueError(message)
        if isinstance(other, MonoChannel):
            other = StereoSound((other, other))
        left_channel = self.left_channel + other.left_channel
        right_channel = self.right_channel + other.right_channel
        return StereoSound((left_channel, right_channel))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StereoSound):
            return False
        equal_left_channel = self.left_channel == other.left_channel
        equal_right_channel = self.right_channel == other.right_channel
        equal_frequency = self.sampling_frequency == other.sampling_frequency
        return equal_left_channel and equal_right_channel and equal_frequency

    def time_frame(self, start: float, stop: float = None) -> 'StereoSound':
        left_channel = self.left_channel.time_frame(start, stop)
        right_channel = self.right_channel.time_frame(start, stop)
        return StereoSound((left_channel, right_channel))


def test():
    filepath = Path(r'audios/a1_com_ruido.wav')
    sampling_frequency, audio = wavfile.read(filepath, 'r')
    left_channel = MonoChannel(audio[:, 0], sampling_frequency)
    right_channel = MonoChannel(audio[:, 1], sampling_frequency)
    stereo_tuple = StereoSound((left_channel, right_channel))
    stereo_path = StereoSound(filepath)
    print(stereo_tuple, stereo_path, sep='\n')
    print((stereo_tuple + left_channel).left_channel.audio.size)
    print(stereo_tuple == stereo_path)


if __name__ == '__main__':
    test()
