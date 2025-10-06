# hand_tracker.py
import cv2
import mediapipe as mp
from settings import MIN_DET_CONF, MIN_TRK_CONF

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

class HandTracker:
    def __init__(self, max_num_hands=1):
        self.h = mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=MIN_DET_CONF,
            min_tracking_confidence=MIN_TRK_CONF
        )

    def process(self, bgr_frame):
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        result = self.h.process(rgb)
        return result

    @staticmethod
    def draw(frame, result):
        if result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame, result.multi_hand_landmarks[0],
                mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style()
            )
