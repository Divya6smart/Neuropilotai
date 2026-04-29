import pyautogui
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionController:
    def __init__(self):
        # Failsafe will abort if mouse is moved to the corner
        pyautogui.FAILSAFE = True
        
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to specific coordinates."""
        logger.info(f"Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y, duration=duration)

    def click(self, x: int = None, y: int = None, clicks: int = 1, button: str = 'left'):
        """Click at current or specified coordinates."""
        if x is not None and y is not None:
            self.move_to(x, y)
        logger.info(f"Clicking {button} button {clicks} times.")
        pyautogui.click(clicks=clicks, button=button)

    def type_text(self, text: str, interval: float = 0.05):
        """Type text sequentially."""
        logger.info(f"Typing text: {text}")
        pyautogui.write(text, interval=interval)

    def press_key(self, key: str):
        """Press a specific keyboard key."""
        logger.info(f"Pressing key: {key}")
        pyautogui.press(key)
        
    def hotkey(self, *keys):
        """Press a combination of keys (e.g., 'ctrl', 'c')."""
        logger.info(f"Pressing hotkey: {keys}")
        pyautogui.hotkey(*keys)

    def scroll(self, amount: int):
        """Scroll up or down. Positive for up, negative for down."""
        logger.info(f"Scrolling by {amount}")
        pyautogui.scroll(amount)

action_controller = ActionController()
