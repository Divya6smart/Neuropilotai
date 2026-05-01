import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import os

# Attempt to find Tesseract on Windows
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Users\\' + os.getlogin() + r'\AppData\Local\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
]

for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

class VisionEngine:
    def __init__(self):
        pass

    def capture_screen(self):
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_text_on_screen(self, target_text):
        """
        Optimized OCR search: Resizes image and pre-processes for speed.
        """
        screenshot = pyautogui.screenshot()
        # Resize image to improve speed (2x smaller)
        width, height = screenshot.size
        new_size = (width // 2, height // 2)
        small_img = screenshot.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to grayscale and thresholding for better/faster OCR
        open_cv_image = np.array(small_img)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Get OCR data
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        
        matches = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if target_text.lower() in data['text'][i].lower():
                # Map coordinates back to original size
                x = data['left'][i] * 2
                y = data['top'][i] * 2
                w = data['width'][i] * 2
                h = data['height'][i] * 2
                center_x = x + w // 2
                center_y = y + h // 2
                matches.append((center_x, center_y))
        
        if not matches:
            return None
        
        # If multiple matches, find the one closest to the center of the screen
        screen_width, screen_height = pyautogui.size()
        screen_center = (screen_width // 2, screen_height // 2)
        
        closest_match = min(matches, key=lambda pos: (pos[0] - screen_center[0])**2 + (pos[1] - screen_center[1])**2)
        return closest_match

    def click_text(self, text):
        coords = self.find_text_on_screen(text)
        if coords:
            pyautogui.moveTo(coords[0], coords[1], duration=0.5)
            pyautogui.click()
            return True
        return False
if __name__ == "__main__":
    engine = VisionEngine()
    print("Capturing screen...")
    screenshot = engine.capture_screen()
    print(f"Screenshot shape: {screenshot.shape}")
    
    # Test OCR
    test_text = "Recycle" # Common on desktops
    print(f"Searching for text: '{test_text}'")
    coords = engine.find_text_on_screen(test_text)
    if coords:
        print(f"Found at: {coords}")
    else:
        print("Text not found.")
