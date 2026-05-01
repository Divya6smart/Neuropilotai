import subprocess
import pyautogui
import webbrowser
import os
import time

class SystemController:
    def __init__(self):
        self.common_apps = {
            "chrome": "start chrome",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "terminal": "start powershell",
            "code": "code",
            "browser": "start chrome",
            "excel": "start excel",
            "word": "start winword"
        }

    def open_app(self, app_name):
        """Robust application opener using shell execution."""
        app_name = app_name.lower().strip()
        print(f"[SystemController] Attempting to open: {app_name}")
        
        # Check dictionary first
        for app, cmd in self.common_apps.items():
            if app in app_name:
                print(f"[SystemController] Match found: {app} -> {cmd}")
                try:
                    subprocess.Popen(cmd, shell=True)
                    return True
                except Exception as e:
                    print(f"[SystemController] Error: {e}")
        
        # Fallback to direct name
        try:
            print(f"[SystemController] Falling back to direct start: {app_name}")
            subprocess.Popen(f"start {app_name}", shell=True)
            return True
        except Exception as e:
            print(f"[SystemController] Fallback Error: {e}")
            return False

    def play_music(self):
        print("[SystemController] Playing music...")
        webbrowser.open("https://www.youtube.com/results?search_query=lofi+hip+hop")
        return True

    def open_reels(self):
        print("[SystemController] Opening reels...")
        webbrowser.open("https://www.instagram.com/reels/")
        return True

    def create_folder(self, folder_name="New Folder"):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, folder_name)
        print(f"[SystemController] Creating folder at: {path}")
        if not os.path.exists(path):
            os.makedirs(path)
            return True
        return False

    def write_document(self, text):
        print(f"[SystemController] Writing document: {text}")
        subprocess.Popen("notepad.exe")
        time.sleep(1.5)
        pyautogui.write(text, interval=0.01)
        return True

    def close_app(self):
        print("[SystemController] Closing app...")
        pyautogui.hotkey('alt', 'f4')
        return True

    def search_web(self, query):
        print(f"[SystemController] Searching web: {query}")
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return True
