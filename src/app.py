import time
import cv2

from settings import *
from camera_stream import open_camera, read_frame, show, key, close
from hand_tracker import HandTracker
from calibrator import Calibrator
from gestures import pinch, scroll_mode
from controller import CursorController

class HandLandmark:
    THUMB_TIP = 4
    INDEX_FINGER_TIP = 8
    INDEX_FINGER_PIP = 6
    MIDDLE_FINGER_TIP = 12
    MIDDLE_FINGER_PIP = 10

def clamp(v, lo, hi): return max(lo, min(hi, v))
def lerp(a, b, t): return a + (b - a) * t

def map_to_screen(nx, ny, calib):
    if not calib.calibrated:
        return int(nx * controller.screen_w), int(ny * controller.screen_h)
    rx = (nx - calib.min[0]) / max(1e-6, (calib.max[0]-calib.min[0]))
    ry = (ny - calib.min[1]) / max(1e-6, (calib.max[1]-calib.min[1]))
    rx = clamp(rx, 0.0, 1.0); ry = clamp(ry, 0.0, 1.0)
    return int(rx * controller.screen_w), int(ry * controller.screen_h)

def draw_calibration_overlay(frame, calib):
    progress = calib.progress()
    cv2.putText(frame, "Calibration in progress",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    cv2.putText(frame, "Move your index finger around the camera view",
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Cover top, bottom, left, and right areas",
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Progress: {progress}%",
                (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

if __name__ == "__main__":
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 960, 720)
    cap = open_camera(CAMERA_INDEX)
    tracker = HandTracker(max_num_hands=1)
    controller = CursorController()
    calib = Calibrator(collect_seconds=5.0)

    t0 = time.time(); fps = 0.0

    from splash import show_until_space
    if not show_until_space(lambda: read_frame(cap)):
        close(cap); exit()

    calib.start()
    sx = sy = None

    while True:
        frame = read_frame(cap)
        if frame is None:
            continue

        result = tracker.process(frame)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0]
            idx_tip = lm[HandLandmark.INDEX_FINGER_TIP]

            if calib.collecting:
                calib.step(idx_tip.x, idx_tip.y)
                draw_calibration_overlay(frame, calib)
            elif calib.calibrated:
                cv2.putText(frame, "Calibration complete",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            tx, ty = map_to_screen(idx_tip.x, idx_tip.y, calib)
            if sx is None:
                sx, sy = tx, ty
            else:
                if abs(tx - sx) > 20 or abs(ty - sy) > 20:
                    sx = int(lerp(sx, tx, 1.0 - SMOOTHING))
                    sy = int(lerp(sy, ty, 1.0 - SMOOTHING))

            is_pinch = pinch(lm, HandLandmark)
            in_scroll = scroll_mode(lm, HandLandmark)

            controller.move(sx, sy)
            controller.handle_pinch(is_pinch)
            controller.handle_scroll(in_scroll, sy)

            HandTracker.draw(frame, result)
        else:
            controller.release_all()

        if SHOW_FPS:
            t = time.time()
            fps = 0.9*fps + 0.1*(1.0 / max(1e-6, t - t0))
            t0 = t
            cv2.putText(frame, f"FPS: {fps:.1f}", (20, frame.shape[0]-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)
        cv2.putText(frame, "Keys: SPACE(splash)  c=calibrate  r=reset  q=quit",
                    (20, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180,180,180), 2)

        show(WINDOW_NAME, frame)
        k = key(1)
        if k == ord('q'):
            break
        elif k == ord('c'):
            calib.start()
        elif k == ord('r'):
            calib.reset()
        elif k == 32:
            from splash import show_until_space
            if not show_until_space(lambda: read_frame(cap)):
                break

    controller.release_all()
    close(cap)