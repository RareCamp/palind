import numpy as np


def similarity(a, b) -> float:
    assert len(a) == len(b)
    assert len(a) > 0
    a = np.array(list(map(int, list(a))))
    b = np.array(list(map(int, list(b))))
    return (a == b).sum() / len(a)
