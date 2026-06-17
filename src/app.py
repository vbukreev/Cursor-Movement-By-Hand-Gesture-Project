import time
import cv2
import mediapipe as mp

from settings import *
from camera_stream import open_camera, read_frame, show, key, close
from hand_tracker import HandTracker
from calibrator import Calibrator
from gestures import pinch, scroll_mode
from controller import CursorController


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def draw_calibration_bar(frame, calib):
    h, w = frame.shape[:2]

    bar_x1 = 50
    bar_y1 = 80
    bar_x2 = w - 50
    bar_y2 = 120

    if calib.collecting:
        progress = calib.progress()
        text = f"Calibration: {int(progress * 100)}%"
        fill_color = (0, 255, 255)

    elif calib.calibrated:
        progress = 1.0
        text = "Calibration Complete"
        fill_color = (0, 255, 0)

    else:
        progress = 0.0
        text = "Press C to start calibration"
        fill_color = (80, 80, 80)

    cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (0, 0, 0), -1)
    cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (255, 255, 255), 2)

    fill_width = int((bar_x2 - bar_x1) * progress)

    if fill_width > 0:
        cv2.rectangle(
            frame,
            (bar_x1, bar_y1),
            (bar_x1 + fill_width, bar_y2),
            fill_color,
            -1,
        )

    cv2.putText(
        frame,
        text,
        (bar_x1, bar_y1 - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 255),
        2,
    )


def draw_roi(frame, calib):
    if not calib.calibrated:
        return

    x1 = int(calib.min[0] * frame.shape[1])
    y1 = int(calib.min[1] * frame.shape[0])
    x2 = int(calib.max[0] * frame.shape[1])
    y2 = int(calib.max[1] * frame.shape[0])

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)


def map_to_screen(nx, ny, calib, controller):
    margin = 10

    if not calib.calibrated:
        sx = int(nx * (controller.screen_w - 2 * margin)) + margin
        sy = int(ny * (controller.screen_h - 2 * margin)) + margin
        return sx, sy

    rx = (nx - calib.min[0]) / max(1e-6, (calib.max[0] - calib.min[0]))
    ry = (ny - calib.min[1]) / max(1e-6, (calib.max[1] - calib.min[1]))

    rx = clamp(rx, 0.0, 1.0)
    ry = clamp(ry, 0.0, 1.0)

    sx = int(rx * (controller.screen_w - 2 * margin)) + margin
    sy = int(ry * (controller.screen_h - 2 * margin)) + margin

    return sx, sy


if __name__ == "__main__":
    cap = open_camera(CAMERA_INDEX)
    tracker = HandTracker(max_num_hands=1)
    controller = CursorController()
    calib = Calibrator(collect_seconds=3.0)

    t0 = time.time()
    fps = 0.0

    from splash import show_until_space

    def get_frame_for_splash():
        return read_frame(cap)

    if not show_until_space(get_frame_for_splash):
        close(cap)
        exit()

    sx = sy = None

    while True:
        frame = read_frame(cap)

        if frame is None:
            break

        result = tracker.process(frame)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            idx_tip = lm[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

            if calib.collecting:
                calib.step(idx_tip.x, idx_tip.y)

            tx, ty = map_to_screen(idx_tip.x, idx_tip.y, calib, controller)

            if sx is None:
                sx, sy = tx, ty
            else:
                sx = int(lerp(sx, tx, 1.0 - SMOOTHING))
                sy = int(lerp(sy, ty, 1.0 - SMOOTHING))

            is_pinch = pinch(lm, mp.solutions.hands.HandLandmark)
            in_scroll = scroll_mode(lm, mp.solutions.hands.HandLandmark)

            controller.move(sx, sy)
            controller.handle_pinch(is_pinch)
            controller.handle_scroll(in_scroll, sy)

            HandTracker.draw(frame, result)
            draw_roi(frame, calib)

        else:
            controller.release_all()

        draw_calibration_bar(frame, calib)

        if SHOW_FPS:
            t = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, t - t0))
            t0 = t

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                2,
            )

        cv2.putText(
            frame,
            "Keys: C = calibrate | R = reset | SPACE = splash | Q = quit",
            (20, frame.shape[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (180, 180, 180),
            2,
        )

        show(WINDOW_NAME, frame)

        k = key(1)

        if k == ord("q"):
            break

        if k == ord("c"):
            calib.start()
            sx = sy = None

        if k == ord("r"):
            calib.reset()
            sx = sy = None

        if k == 32:
            if not show_until_space(lambda: read_frame(cap)):
                break

    controller.release_all()
    close(cap)