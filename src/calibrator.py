# calibrator.py
import time
from settings import CALIB_INIT_MIN, CALIB_INIT_MAX

class Calibrator:
    def __init__(self, collect_seconds=3.0):
        self.calibrated = False
        self.min = CALIB_INIT_MIN[:]
        self.max = CALIB_INIT_MAX[:]
        self.collecting = False
        self.t0 = 0.0
        self.dur = collect_seconds

    def start(self):
        self.calibrated = False
        self.min = [1.0, 1.0]
        self.max = [0.0, 0.0]
        self.collecting = True
        self.t0 = time.time()

    def reset(self):
        self.calibrated = False
        self.collecting = False
        self.min = CALIB_INIT_MIN[:]
        self.max = CALIB_INIT_MAX[:]

    def step(self, nx, ny):
        """Call while collecting; pass normalized fingertip."""
        if not self.collecting:
            return 0.0
        t = time.time() - self.t0
        if t < self.dur:
            self.min[0] = min(self.min[0], nx)
            self.min[1] = min(self.min[1], ny)
            self.max[0] = max(self.max[0], nx)
            self.max[1] = max(self.max[1], ny)
            return self.dur - t
        else:
            self.collecting = False
            self.calibrated = True
            return 0.0
