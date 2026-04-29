from typing import List, Dict

class PlannerAgent:
    def __init__(self):
        pass

    def plan_task(self, instruction: str) -> List[Dict]:
        """
        Breaks down a high-level instruction into actionable steps.
        In a real system, this calls an LLM. Here, we mock the behavior.
        """
        print(f"Planner: Breaking down task '{instruction}'")
        
        # Mock logic for planning
        if "notepad" in instruction.lower():
            return [
                {"action_type": "hotkey", "params": ["win"]},
                {"action_type": "type", "params": {"text": "notepad"}},
                {"action_type": "press", "params": {"key": "enter"}},
                {"action_type": "wait", "params": {"duration": 2}},
                {"action_type": "type", "params": {"text": "Hello World!"}}
            ]
        elif "youtube" in instruction.lower():
            return [
                {"action_type": "hotkey", "params": ["win"]},
                {"action_type": "type", "params": {"text": "chrome"}},
                {"action_type": "press", "params": {"key": "enter"}},
                {"action_type": "wait", "params": {"duration": 2}},
                {"action_type": "type", "params": {"text": "youtube.com"}},
                {"action_type": "press", "params": {"key": "enter"}}
            ]
        
        return [
            {"action_type": "log", "params": {"msg": f"No plan found for: {instruction}"}}
        ]

planner_agent = PlannerAgent()
