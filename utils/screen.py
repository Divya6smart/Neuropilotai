import cv2
import numpy as np
from PIL import ImageGrab
import os

class ScreenManager:
    def __init__(self, save_dir="data/screenshots"):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        
    def capture_screen(self, filename="latest.png"):
        """Captures the entire screen and saves it as an image."""
        screenshot = ImageGrab.grab()
        filepath = os.path.join(self.save_dir, filename)
        screenshot.save(filepath)
        return filepath
        
    def get_screen_np(self):
        """Returns the screen as a numpy array for OpenCV processing."""
        screenshot = ImageGrab.grab()
        img_np = np.array(screenshot)
        # Convert RGB to BGR for OpenCV
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

screen_manager = ScreenManager()
