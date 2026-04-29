import cv2
import pytesseract
import numpy as np

# Ensure tesseract is in PATH or configure it here:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class VisionSystem:
    def __init__(self):
        pass

    def extract_text_and_boxes(self, image_path: str):
        """
        Reads an image and returns detected text along with bounding boxes.
        Returns a list of dicts: {'text': str, 'x': int, 'y': int, 'w': int, 'h': int}
        """
        img = cv2.imread(image_path)
        if img is None:
            return []
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Use pytesseract to get data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        elements = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60: # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    elements.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'w': data['width'][i],
                        'h': data['height'][i]
                    })
                    
        return elements

    def find_element_by_text(self, image_path: str, target_text: str):
        """Finds the bounding box of a specific text on the screen."""
        elements = self.extract_text_and_boxes(image_path)
        for el in elements:
            if target_text.lower() in el['text'].lower():
                return el
        return None

vision_system = VisionSystem()
