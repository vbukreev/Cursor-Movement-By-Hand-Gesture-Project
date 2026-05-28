# app.py
import time
import cv2
import mediapipe as mp

from settings import *
from camera_stream import open_camera, read_frame, show, key, close
from hand_tracker import HandTracker
from calibrator import Calibrator
from gestures import pinch, scroll_mode
from controller import CursorController

def clamp(v, lo, hi): return max(lo, min(hi, v))
def lerp(a, b, t): return a + (b - a) * t

def map_to_screen(nx, ny, calib):
    if not calib.calibrated:
        return int(nx * controller.screen_w), int(ny * controller.screen_h)
    rx = (nx - calib.min[0]) / max(1e-6, (calib.max[0]-calib.min[0]))
    ry = (ny - calib.min[1]) / max(1e-6, (calib.max[1]-calib.min[1]))
    rx = clamp(rx, 0.0, 1.0); ry = clamp(ry, 0.0, 1.0)
    return int(rx * controller.screen_w), int(ry * controller.screen_h)

if __name__ == "__main__":
    cap = open_camera(CAMERA_INDEX)
    tracker = HandTracker(max_num_hands=1)
    controller = CursorController()
    calib = Calibrator(collect_seconds=3.0)

    # simple fps
    t0 = time.time(); fps = 0.0

    # splash with crossfade
    from splash import show_until_space
    def get_frame_for_splash():
        f = read_frame(cap)
        return f
    if not show_until_space(get_frame_for_splash):
        close(cap); exit()

    sx = sy = None

    while True:
        frame = read_frame(cap)
        if frame is None:
            break

        result = tracker.process(frame)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            idx_tip = lm[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

            # calibration collection
            if calib.collecting:
                remaining = calib.step(idx_tip.x, idx_tip.y)
                cv2.putText(frame, f"Calibrating... move fingertip ({remaining:.1f}s)",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,255), 2)

            # map & smooth
            tx, ty = map_to_screen(idx_tip.x, idx_tip.y, calib)
            if sx is None:
                sx, sy = tx, ty
            else:
                sx = int(lerp(sx, tx, 1.0 - SMOOTHING))
                sy = int(lerp(sy, ty, 1.0 - SMOOTHING))

            # gestures
            is_pinch = pinch(lm, mp.solutions.hands.HandLandmark)
            in_scroll = scroll_mode(lm, mp.solutions.hands.HandLandmark)

            # apply
            controller.move(sx, sy)
            controller.handle_pinch(is_pinch)
            controller.handle_scroll(in_scroll, sy)

            # draw landmarks + ROI
            HandTracker.draw(frame, result)
            if calib.calibrated:
                x1 = int(calib.min[0] * frame.shape[1])
                y1 = int(calib.min[1] * frame.shape[0])
                x2 = int(calib.max[0] * frame.shape[1])
                y2 = int(calib.max[1] * frame.shape[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,255), 2)
        else:
            # lost hand → release drag
            controller.release_all()

        # HUD
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
        elif k == 32:  # space → show splash again, then crossfade back
            from splash import show_until_space
            if not show_until_space(lambda: read_frame(cap)):
                break

    controller.release_all()
    close(cap)
