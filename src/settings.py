# settings.py
CAMERA_INDEX = 1  # change if needed
MIN_DET_CONF = 0.6
MIN_TRK_CONF = 0.5

SMOOTHING = 0.35           # 0..1 (higher = smoother)
PINCH_THRESH = 0.055       # thumb-index distance (normalized)
SCROLL_GAIN = 180          # scroll speed
DRAG_HOLD_SECONDS = 0.3
CLICK_DEBOUNCE = 0.25

SHOW_FPS = True
WINDOW_NAME = "Hand Cursor"

# splash + transition
SPLASH_TEXT = "Cursor by Hand Gesture\nPress SPACE to start"
SPLASH_HINT = "c=calibrate  r=reset  q=quit"
CROSSFADE_FRAMES = 18      # frames for splash→camera crossfade

# initial calibration bounding box (when not calibrated yet)
CALIB_INIT_MIN = [0.30, 0.30]
CALIB_INIT_MAX = [0.70, 0.70]
