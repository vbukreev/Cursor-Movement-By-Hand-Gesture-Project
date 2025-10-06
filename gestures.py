# gestures.py
import math
from settings import PINCH_THRESH

def norm_dist(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.hypot(dx, dy)

def pinch(lm, hands):
    idx_tip = lm[hands.INDEX_FINGER_TIP]
    thm_tip = lm[hands.THUMB_TIP]
    return norm_dist(idx_tip, thm_tip) < PINCH_THRESH

def fingers_up(lm, hands):
    idx_tip = lm[hands.INDEX_FINGER_TIP]
    idx_pip = lm[hands.INDEX_FINGER_PIP]
    mid_tip = lm[hands.MIDDLE_FINGER_TIP]
    mid_pip = lm[hands.MIDDLE_FINGER_PIP]
    index_up  = idx_tip.y < idx_pip.y
    middle_up = mid_tip.y < mid_pip.y
    return index_up, middle_up

def scroll_mode(lm, hands):
    # two finger “V” and thumb not pinched
    idx_up, mid_up = fingers_up(lm, hands)
    thm_tip = lm[hands.THUMB_TIP]
    idx_tip = lm[hands.INDEX_FINGER_TIP]
    return idx_up and mid_up and (norm_dist(thm_tip, idx_tip) > PINCH_THRESH*1.2)
