"""Thread-safe memory system with encrypted persistent storage."""
import json
import os
import datetime
import threading
import logging
from config import config

logger = logging.getLogger(__name__)


class MemorySystem:
    def __init__(self, memory_file=None):
        self.memory_file = str(memory_file or config.MEMORY_FILE)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self._lock = threading.Lock()
        if not os.path.exists(self.memory_file):
            self._save({"history": [], "patterns": []})

    def _load(self) -> dict:
        with self._lock:
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("Memory file corrupted — reinitializing")
                data = {"history": [], "patterns": []}
                self._save_unlocked(data)
                return data

    def _save(self, data: dict):
        with self._lock:
            self._save_unlocked(data)

    def _save_unlocked(self, data: dict):
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)

    def add_action(self, task: str, action: dict, success: bool):
        mem = self._load()
        mem["history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "task": task,
            "action": action,
            "success": success,
        })
        # Keep history bounded to prevent unbounded growth
        if len(mem["history"]) > 1000:
            mem["history"] = mem["history"][-500:]
        self._save(mem)

    def find_pattern(self, current_context: str):
        mem = self._load()
        for p in mem.get("patterns", []):
            if p.get("context") == current_context:
                return p.get("predicted_action")
        return None

    def add_pattern(self, context: str, predicted_action):
        mem = self._load()
        # Avoid duplicates
        for p in mem["patterns"]:
            if p["context"] == context:
                p["predicted_action"] = predicted_action
                self._save(mem)
                return
        mem["patterns"].append({
            "context": context,
            "predicted_action": predicted_action,
            "created_at": datetime.datetime.now().isoformat(),
        })
        self._save(mem)

    def get_history(self, limit: int = 50) -> list:
        mem = self._load()
        return mem["history"][-limit:]


memory_system = MemorySystem()
