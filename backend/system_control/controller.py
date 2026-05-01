import subprocess
import pyautogui
import webbrowser
import os
import time

class SystemController:
    def __init__(self):
        pass

    def open_app(self, app_name):
        """Opens common applications."""
        app_name = app_name.lower()
        if "chrome" in app_name:
            webbrowser.open("https://www.google.com")
        elif "notepad" in app_name:
            subprocess.Popen("notepad.exe")
        elif "terminal" in app_name or "cmd" in app_name:
            subprocess.Popen("cmd.exe")
        elif "calculator" in app_name:
            subprocess.Popen("calc.exe")
        else:
            # Fallback: try to run it via start command
            try:
                os.system(f"start {app_name}")
            except Exception as e:
                print(f"Error opening {app_name}: {e}")

    def play_music(self):
        """Opens YouTube music or similar."""
        webbrowser.open("https://www.youtube.com/results?search_query=lofi+hip+hop")
        time.sleep(3)
        # Try to press space to play if it doesn't auto-play
        pyautogui.press('space')

    def open_reels(self):
        webbrowser.open("https://www.instagram.com/reels/")

    def create_folder(self, folder_name="New Folder"):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
            return True
        return False

    def send_message(self, message, contact):
        # Very basic WhatsApp Web mock or similar
        webbrowser.open(f"https://web.whatsapp.com/send?text={message}")
        # Requires user to be logged in and manual click for now or more complex automation

    def write_document(self, text):
        subprocess.Popen("notepad.exe")
        time.sleep(1)
        pyautogui.write(text, interval=0.01)

    def close_app(self):
        pyautogui.hotkey('alt', 'f4')
