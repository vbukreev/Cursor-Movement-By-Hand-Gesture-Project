import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from gestures import norm_dist


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_norm_dist_zero():
    a = Point(0, 0)
    b = Point(0, 0)
    assert norm_dist(a, b) == 0


def test_norm_dist_positive():
    a = Point(0, 0)
    b = Point(3, 4)
    assert norm_dist(a, b) == 5