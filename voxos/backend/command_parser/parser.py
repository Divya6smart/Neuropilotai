import re

class CommandParser:
    def __init__(self):
        self.intent_map = {
            "open": "open_app",
            "play": "play_music",
            "create": "create_folder",
            "reels": "open_reels",
            "send": "send_message",
            "write": "write_document",
            "click": "click_text",
            "type": "type_text",
            "close": "close_app"
        }

    def split_commands(self, text):
        """Splits text and removes wake words anywhere they appear."""
        text = text.lower().strip()
        # Remove common wake words anywhere they appear
        text = re.sub(r'\b(voxos|jarvis|hey jarvis|hey voxos)\b', '', text).strip()
        
        # Split by keywords
        parts = re.split(r'\s+and\s+|\s+then\s+|,\s*', text)
        return [p.strip() for p in parts if p.strip()]

    def parse(self, command):
        """Parses a single command string into a structured task."""
        command = command.lower()
        
        if "click" in command:
            target = command.split("click")[-1].strip()
            return {"action": "click_text", "params": target}
            
        for keyword, action in self.intent_map.items():
            if keyword in command:
                params = command.split(keyword)[-1].strip()
                return {"action": action, "params": params}
        
        return {"action": "unknown", "params": command}
