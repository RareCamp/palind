import numpy as np


def dice(a, b) -> float:
    assert len(a) == len(b)
    assert len(a) > 0
    a = np.array(list(map(int, list(a))))
    b = np.array(list(map(int, list(b))))
    return 2 * (a & b).sum() / (a.sum() + b.sum())


def similarity(a, b) -> float:
    assert len(a) == len(b)
    assert len(a) > 0
    a = np.array(list(map(int, list(a))))
    b = np.array(list(map(int, list(b))))
    return (a == b).sum() / len(a)
