# controller.py
import pyautogui
import time
from settings import SCROLL_GAIN, CLICK_DEBOUNCE  # <-- Ensure these are imported

class CursorController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()  # Initialize screen width and height here
        self.dragging = False
        self.pinch_down = False
        self.pinch_t0 = 0.0
        self.last_click = 0.0
        self.last_scroll_y = None

    def move(self, x, y):
        pyautogui.moveTo(x, y, _pause=False)

    def handle_pinch(self, is_pinch):
        now = time.time()
        if is_pinch and not self.pinch_down:
            self.pinch_down = True
            self.pinch_t0 = now
        elif not is_pinch and self.pinch_down:
            self.pinch_down = False
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False
            else:
                if now - self.last_click > CLICK_DEBOUNCE:
                    pyautogui.click()
                    self.last_click = now

    def handle_scroll(self, in_scroll_mode, sy, gain=SCROLL_GAIN):
        if in_scroll_mode:
            if self.last_scroll_y is None:
                self.last_scroll_y = sy
            else:
                dy = sy - self.last_scroll_y
                if abs(dy) > 2:
                    pyautogui.scroll(int(-dy * (gain / 100.0)))
                self.last_scroll_y = sy
        else:
            self.last_scroll_y = None

    def release_all(self):
        if self.dragging:
            pyautogui.mouseUp()
            self.dragging = False
