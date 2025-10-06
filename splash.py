# splash.py
import cv2
import numpy as np
from settings import SPLASH_TEXT, SPLASH_HINT, CROSSFADE_FRAMES, WINDOW_NAME

def make_splash(size, bg=(20,20,20)):
    h, w = size
    img = np.full((h, w, 3), bg, dtype=np.uint8)
    # title
    y0 = int(h*0.35)
    cv2.putText(img, SPLASH_TEXT, (40, y0), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (230,230,230), 2, cv2.LINE_AA)
    # hint
    cv2.putText(img, SPLASH_HINT, (40, y0+40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180,180,180), 2, cv2.LINE_AA)
    cv2.putText(img, "Press SPACE to begin", (40, y0+80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,200,255), 2, cv2.LINE_AA)
    return img

def show_until_space(frame_provider):
    """
    frame_provider(): returns latest camera frame (for sizing); not shown yet.
    Wait SPACE, then crossfade splash → first camera frames.
    """
    # get one frame for size
    base = frame_provider()
    if base is None:
        raise RuntimeError("No camera frame available for splash sizing.")
    h, w = base.shape[:2]
    splash = make_splash((h, w))

    while True:
        # draw splash (static)
        cv2.imshow(WINDOW_NAME, splash)
        k = cv2.waitKey(1) & 0xFF
        if k == 32:  # SPACE
            break
        elif k == ord('q'):
            return False

    # crossfade
    for i in range(CROSSFADE_FRAMES):
        cam = frame_provider()
        if cam is None:
            cam = base
        alpha = (i+1)/float(CROSSFADE_FRAMES)
        blend = cv2.addWeighted(cam, alpha, splash, 1.0-alpha, 0.0)
        cv2.imshow(WINDOW_NAME, blend)
        cv2.waitKey(1)
    return True
