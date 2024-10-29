from dataclasses import dataclass

import numpy as np

DEFAULT_NUMTAPS = 71


@dataclass()
class Equalizer:
    numtaps: int
    gain: np.ndarray
    frequencies: np.ndarray

    def __init__(self, frequencies: np.ndarray, gain_db: np.ndarray,
                 numtaps: int = DEFAULT_NUMTAPS) -> None:
        self.numtaps = numtaps
        self.gain = np.power(10, gain_db/10)
        self.frequencies = frequencies
        self._validade_frequencies()
        if self.frequencies.size != self.gain.size:
            message = 'gain and frequency arrays must have the same size.'
            raise ValueError(message)

    def _validade_frequencies(self) -> None:
        if self.frequencies.size < 2:
            message = 'frequency array must have at least two frequencies.'
            raise ValueError(message)
        if self.frequencies[0] != 0:
            raise ValueError('frequency array must start with 0.')
        if np.any(self.frequencies != np.sort(self.frequencies)):
            raise ValueError('frequency array must be nondecreasing.')


def test():
    x = Equalizer(1, np.arange(3), np.arange(3))
    print(x)


if __name__ == '__main__':
    test()
