"""Executor agent with retry logic and self-healing."""
import time
import logging
from utils.actions import action_controller
from utils.screen import screen_manager
from agent.vision import vision_system

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 1.5  # seconds multiplier per retry


class ExecutorAgent:
    def __init__(self):
        self.action = action_controller

    def execute_step(self, step: dict, retries: int = MAX_RETRIES) -> bool:
        """Execute a step with automatic retry and exponential backoff."""
        action_type = step.get("action_type")
        params = step.get("params", {})

        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Executing {action_type} (attempt {attempt}/{retries})")
                self._dispatch(action_type, params)
                return True
            except Exception as e:
                logger.warning(f"Step failed (attempt {attempt}): {e}")
                if attempt < retries:
                    wait = RETRY_BACKOFF * attempt
                    logger.info(f"Retrying in {wait:.1f}s...")
                    time.sleep(wait)

        logger.error(f"Step {action_type} failed after {retries} attempts")
        return False

    def _dispatch(self, action_type: str, params):
        """Route action to the correct controller method."""
        if action_type == "move":
            self.action.move_to(params["x"], params["y"])
        elif action_type == "click":
            self.action.click(params.get("x"), params.get("y"))
        elif action_type == "type":
            self.action.type_text(params["text"])
        elif action_type == "press":
            self.action.press_key(params["key"])
        elif action_type == "hotkey":
            if isinstance(params, list):
                self.action.hotkey(*params)
            else:
                self.action.hotkey(*params.values())
        elif action_type == "wait":
            time.sleep(params.get("duration", 1))
        elif action_type == "find_and_click":
            img_path = screen_manager.capture_screen()
            el = vision_system.find_element_by_text(img_path, params["target_text"])
            if el:
                cx = el["x"] + el["w"] // 2
                cy = el["y"] + el["h"] // 2
                self.action.click(cx, cy)
            else:
                raise RuntimeError(f"Element '{params['target_text']}' not found on screen")
        elif action_type == "log":
            logger.info(params.get("msg", ""))
        else:
            logger.warning(f"Unknown action: {action_type}")


executor_agent = ExecutorAgent()
