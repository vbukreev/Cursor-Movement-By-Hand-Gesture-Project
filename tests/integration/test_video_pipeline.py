# tests/integration/test_video_pipeline.py
import cv2
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

VIDEO_PATH = os.path.join(os.path.dirname(__file__), '../../tests/fixtures/test_hand.mp4')


@pytest.fixture
def video_frames():
    if not os.path.exists(VIDEO_PATH):
        pytest.skip("Test video not found — skipping video pipeline test")
    cap = cv2.VideoCapture(VIDEO_PATH)
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    return frames


def test_video_loads_successfully(video_frames):
    """Video must load and contain at least 30 frames."""
    assert len(video_frames) >= 30, "Test video too short"


def test_hand_detected_in_video(video_frames):
    """MediaPipe must detect a hand in at least 50% of frames."""
    import mediapipe as mp
    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detected = 0
    for frame in video_frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        if result.multi_hand_landmarks:
            detected += 1
    hands.close()

    rate = detected / len(video_frames)
    print(f"\nHand detected in {rate:.0%} of frames ({detected}/{len(video_frames)})")
    assert rate >= 0.5, f"Hand only detected in {rate:.0%} of frames — check lighting"


def test_gesture_detection_on_video(video_frames):
    """Gesture functions must not crash on real hand footage."""
    import mediapipe as mp
    from gestures import norm_dist, fingers_up, scroll_mode, pinch

    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
    )
    hands_lm = mp.solutions.hands.HandLandmark
    errors = []

    for i, frame in enumerate(video_frames):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            try:
                pinch(lm, hands_lm)
                scroll_mode(lm, hands_lm)
                fingers_up(lm, hands_lm)
            except Exception as e:
                errors.append(f"Frame {i}: {e}")

    hands.close()
    assert len(errors) == 0, f"Crashed on {len(errors)} frames:\n" + "\n".join(errors[:5])


def test_no_crash_on_empty_frames():
    """App must handle frames with no hand gracefully."""
    import mediapipe as mp
    import numpy as np

    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
    )
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    rgb = cv2.cvtColor(blank, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    hands.close()

    assert result.multi_hand_landmarks is None