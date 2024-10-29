from pathlib import Path
from typing import Any, Union, Tuple, overload

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

import mono as m

Sound = Union['StereoSound', 'm.MonoChannel']
MonoChannelTuple = Tuple['m.MonoChannel', 'm.MonoChannel']


class StereoSound:
    left_channel: 'm.MonoChannel'
    right_channel: 'm.MonoChannel'
    sampling_frequency: 'm.Number'

    @overload
    def __init__(self, audio: Path) -> None:
        pass
    @overload
    def __init__(self, audio: MonoChannelTuple) -> None:
        pass
    def __init__(self, audio):
        if isinstance(audio, Path):
            sampling_frequency, data = wavfile.read(audio, 'r')
            self.left_channel = m.MonoChannel(data[:, 0], sampling_frequency)
            self.right_channel = m.MonoChannel(data[:, 1], sampling_frequency)
            self.sampling_frequency = sampling_frequency
        elif not isinstance(audio, tuple):
            message_11 = 'cannot instantiate class with parameters provided. '
            message_12 = 'Can only take path to .wav file or tuple containing'
            message_13 = ' left and right channels as MonoChannel instances.'
            raise TypeError(''.join((message_11, message_12, message_13)))
        else:
            correct_tuple_types = (
                isinstance(audio[0], m.MonoChannel)
                and isinstance(audio[1], m.MonoChannel)
            )
            if not correct_tuple_types or len(audio) != 2:
                message_21 = 'tuple given must contain exactly two '
                message_22 = 'instances of MonoChannel class.'
                raise ValueError(''.join((message_21, message_22)))
            left_channel, right_channel = audio[0], audio[1]
            if left_channel.length != right_channel.length:
                raise ValueError('channels cannot have different lengths.')
            self.sampling_frequency = left_channel.sampling_frequency
            if self.sampling_frequency != right_channel.sampling_frequency:
                message_31 = 'channels cannot have different '
                message_32 = 'sampling frequencies.'
                raise ValueError(''.join((message_31, message_32)))
            self.left_channel = left_channel
            self.right_channel = right_channel

    @property
    def size(self) -> int:
        return int(self.left_channel.size)

    @property
    def length(self) -> float:
        return self.left_channel.length

    @property
    def time(self) -> float:
        index_size = self.size
        return np.linspace(0, self.length, index_size)
    
    def __repr__(self) -> str:
        freq_text = f'Sampling Frequency: {self.sampling_frequency:.0f} Hz'
        left_text = f'Left Channel Data: {self.left_channel.audio}'
        right_text = f'Right Channel Data: {self.right_channel.audio}'
        return '; '.join((freq_text, left_text, right_text))

    def __sub__(self, other: Sound) -> 'StereoSound':
        if not isinstance(other, (StereoSound, m.MonoChannel)):
            message_11 = f'cannot merge StereoSound and '
            message_12 = f"{type(other).__name__}."
            raise TypeError(''.join((message_11, message_12)))
        if self.sampling_frequency != other.sampling_frequency:
            message_21 = 'cannot merge two audios with '
            message_22 = 'different sampling frequencies.'
            message = ''.join((message_21, message_22))
            raise ValueError(message)
        if isinstance(other, m.MonoChannel):
            stereo_other = other.to_stereo()
        left_channel = self.left_channel - stereo_other.left_channel
        right_channel = self.right_channel - stereo_other.right_channel
        return StereoSound((left_channel, right_channel))

    def __floordiv__(self, other: Sound) -> 'StereoSound':
        if not isinstance(other, (StereoSound, m.MonoChannel)):
            message_11 = f"can't overlap StereoSound and "
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
        if isinstance(other, m.MonoChannel):
            padded_other = padded_other.to_stereo()
        left_channel = m.MonoChannel(
            padded_self.left_channel.audio+padded_other.left_channel.audio,
            self.sampling_frequency
        )
        right_channel = m.MonoChannel(
            padded_self.right_channel.audio+padded_other.right_channel.audio,
            self.sampling_frequency
        )
        return StereoSound((left_channel, right_channel))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StereoSound):
            return False
        equal_left_channel = self.left_channel == other.left_channel
        equal_right_channel = self.right_channel == other.right_channel
        equal_frequency = self.sampling_frequency == other.sampling_frequency
        return equal_left_channel and equal_right_channel and equal_frequency

    def add_padding(
            self, ammount: int,
            is_right_padding: bool = False,
            is_lenght = False) -> 'StereoSound':
        padding_audio = m.MonoChannel(
            ammount, self.sampling_frequency, is_length=is_lenght
        )
        if is_right_padding:
            return self - padding_audio
        return padding_audio - self

    def to_mono(self) -> 'm.MonoChannel':
        left_audio = self.left_channel.audio
        right_audio = self.right_channel.audio
        audio = (left_audio + right_audio) / 2
        return m.MonoChannel(audio, self.sampling_frequency)

    def make_channels_equal(self) -> 'StereoSound':
        mono = self.to_mono()
        return StereoSound((mono, mono))

    def plot_audio(self, start: float = 0, stop: float = None) -> None:
        frame = self.time_frame(start, stop)
        plt.figure()
        plt.plot(frame.time, frame.left_channel.audio)
        plt.plot(frame.time, frame.right_channel.audio)
        plt.show()

    def time_frame(self, start: float, stop: float = None) -> 'StereoSound':
        left_channel = self.left_channel.time_frame(start, stop)
        right_channel = self.right_channel.time_frame(start, stop)
        return StereoSound((left_channel, right_channel))

    def save(self, filepath: Path) -> None:
        left_data = self.left_channel.audio[np.newaxis, :]
        right_data = self.right_channel.audio[np.newaxis, :]
        data = np.concatenate((left_data, right_data), axis=0).T
        data = data*np.iinfo(np.int16).max/np.abs(data).max()
        data = data.astype(np.int16)
        wavfile.write(filepath, self.sampling_frequency, data)


def test():
    from scipy.signal import firwin2, tf2sos, sosfiltfilt, sosfreqz

    filepath = Path(r'audios/see-you-later-203103.wav')
    sampling_frequency, audio = wavfile.read(filepath, 'r')
    left_channel = m.MonoChannel(audio[:, 0], sampling_frequency)
    right_channel = m.MonoChannel(audio[:, 1], sampling_frequency)
    stereo_tuple = StereoSound((left_channel, right_channel))
    stereo_path = StereoSound(filepath)
    print(stereo_tuple, stereo_path, sep='\n')
    print((stereo_tuple - left_channel).left_channel.audio.size)
    print(stereo_tuple == stereo_path)
    
    nyquist = sampling_frequency/2
    frequencies = np.array([0, 60, 150, 400, 1000, 2400, 15000, nyquist])
    frequencies = frequencies/nyquist
    gain = np.power(10, np.array([24, -6, -5, -2, -3, -5, 0, 0])/10)
    print(gain)
    fir_filter = firwin2(71, frequencies, gain, antisymmetric=False)
    print(fir_filter)
    fir_filter_sos = tf2sos(fir_filter, 1)
    filtered_audio_left = sosfiltfilt(fir_filter_sos, left_channel.audio)
    filtered_left = m.MonoChannel(filtered_audio_left, sampling_frequency)
    filtered_audio_right = sosfiltfilt(fir_filter_sos, right_channel.audio)
    filtered_right = m.MonoChannel(filtered_audio_right, sampling_frequency)
    filtered_sound = StereoSound((filtered_left, filtered_right))
    filepath_write = Path(r'audios/see_you_later_filtered.wav')
    print(filtered_sound == stereo_tuple)
    filtered_sound.save(filepath_write)

    w, h = sosfreqz(fir_filter_sos, worN=1500)
    plt.subplot(2, 1, 1)
    db = 20*np.log10(np.maximum(np.abs(h), 1e-5))
    plt.plot(w/np.pi, db)
    plt.ylim(-75, 5)
    plt.grid(True)
    plt.yticks([0, -20, -40, -60])
    plt.ylabel('Gain [dB]')
    plt.title('Frequency Response')
    plt.subplot(2, 1, 2)
    plt.plot(w/np.pi, np.angle(h))
    plt.grid(True)
    plt.yticks([-np.pi, -0.5*np.pi, 0, 0.5*np.pi, np.pi],
            [r'$-\pi$', r'$-\pi/2$', '0', r'$\pi/2$', r'$\pi$'])
    plt.ylabel('Phase [rad]')
    plt.xlabel('Normalized frequency (1.0 = Nyquist)')
    plt.show()

    filtered_sound.plot_audio(0.5, 1)
    stereo_tuple.plot_audio(0.5, 1)
    


if __name__ == '__main__':
    test()
