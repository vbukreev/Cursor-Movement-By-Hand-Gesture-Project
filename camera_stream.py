# camera_stream.py
import cv2
from settings import CAMERA_INDEX, WINDOW_NAME

def open_camera(index=CAMERA_INDEX):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {index}. Try a different index.")
    return cap

def read_frame(cap):
    ok, frame = cap.read()
    if not ok:
        return None
    return cv2.flip(frame, 1)  # mirror view

def show(name, frame):
    cv2.imshow(name, frame)

def key(wait_ms=1):
    return cv2.waitKey(wait_ms) & 0xFF

def close(cap):
    try:
        cap.release()
    finally:
        cv2.destroyAllWindows()
