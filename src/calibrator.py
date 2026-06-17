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
        """Collect normalized fingertip coordinates during calibration."""
        if not self.collecting:
            return 0.0

        elapsed = time.time() - self.t0

        if elapsed < self.dur:
            self.min[0] = min(self.min[0], nx)
            self.min[1] = min(self.min[1], ny)
            self.max[0] = max(self.max[0], nx)
            self.max[1] = max(self.max[1], ny)
            return self.dur - elapsed

        self.collecting = False
        self.calibrated = True
        return 0.0

    def progress(self):
        """Return calibration progress from 0.0 to 1.0."""
        if not self.collecting:
            return 1.0 if self.calibrated else 0.0

        elapsed = time.time() - self.t0
        return min(1.0, elapsed / self.dur)

    def status_text(self):
        if self.collecting:
            return "Calibrating: move your index finger around the camera area"
        if self.calibrated:
            return "Calibration complete"
        return "Press C to start calibration"