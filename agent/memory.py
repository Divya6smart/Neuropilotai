import json
import os
import datetime

class MemorySystem:
    def __init__(self, memory_file="data/memory.json"):
        self.memory_file = memory_file
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump({"history": [], "patterns": []}, f)
                
    def load_memory(self):
        with open(self.memory_file, 'r') as f:
            return json.load(f)
            
    def save_memory(self, data):
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=4)
            
    def add_action(self, task: str, action: dict, success: bool):
        mem = self.load_memory()
        mem["history"].append({
            "timestamp": str(datetime.datetime.now()),
            "task": task,
            "action": action,
            "success": success
        })
        self.save_memory(mem)
        
    def find_pattern(self, current_context: str):
        # Basic predictive logic based on history
        mem = self.load_memory()
        # Mock logic: return predicted task based on context
        for p in mem["patterns"]:
            if p["context"] == current_context:
                return p["predicted_action"]
        return None

memory_system = MemorySystem()
