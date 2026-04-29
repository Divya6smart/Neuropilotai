import time
from utils.actions import action_controller
from utils.screen import screen_manager
from agent.vision import vision_system

class ExecutorAgent:
    def __init__(self):
        self.action = action_controller
        
    def execute_step(self, step: dict) -> bool:
        """Executes a single planned step."""
        try:
            action_type = step.get("action_type")
            params = step.get("params", {})
            
            print(f"Executor: Executing {action_type} with {params}")
            
            if action_type == "move":
                self.action.move_to(params["x"], params["y"])
            elif action_type == "click":
                self.action.click(params.get("x"), params.get("y"))
            elif action_type == "type":
                self.action.type_text(params["text"])
            elif action_type == "press":
                self.action.press_key(params["key"])
            elif action_type == "hotkey":
                self.action.hotkey(*params)
            elif action_type == "wait":
                time.sleep(params.get("duration", 1))
            elif action_type == "find_and_click":
                # Vision-based dynamic execution
                img_path = screen_manager.capture_screen()
                el = vision_system.find_element_by_text(img_path, params["target_text"])
                if el:
                    # Click center of bounding box
                    cx = el['x'] + el['w'] // 2
                    cy = el['y'] + el['h'] // 2
                    self.action.click(cx, cy)
                else:
                    raise Exception(f"Element '{params['target_text']}' not found.")
            else:
                print(f"Unknown action: {action_type}")
            return True
        except Exception as e:
            print(f"Executor Error: {e}")
            return False

executor_agent = ExecutorAgent()
