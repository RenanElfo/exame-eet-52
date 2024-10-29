import numpy as np

from .equalizer import Equalizer


BASS_BOOST = Equalizer(
    np.array([0, 60, 150, 400, 1000, 2400, 15000, 22050]),
    np.array([24, -6, -5, -2, -3, -5, 0, 0]),
    71
)


def test() -> None:
    print(BASS_BOOST)


if __name__ == '__main__':
    test()
