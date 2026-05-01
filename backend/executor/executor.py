import time
import pyttsx3
import threading

class TaskExecutor:
    def __init__(self, system_controller, vision_engine):
        self.controller = system_controller
        self.vision = vision_engine
        self.engine = pyttsx3.init()
        # Set voice properties
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id) # Usually a male voice

    def speak(self, text):
        print(f"VoxOS: {text}")
        
        def _speak_worker(text_to_say):
            try:
                # Local import and initialization to avoid thread conflicts
                import pyttsx3
                local_engine = pyttsx3.init()
                local_engine.say(text_to_say)
                local_engine.runAndWait()
                # Stop the engine to release the loop
                local_engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")
        
        threading.Thread(target=_speak_worker, args=(text,), daemon=True).start()

    def execute_tasks(self, tasks):
        results = []
        for task in tasks:
            action = task['action']
            params = task['params']
            
            self.speak(f"Executing {action} for {params or 'system'}")
            
            try:
                if action == "open_app":
                    self.controller.open_app(params)
                    results.append(f"Opened {params}")
                elif action == "play_music":
                    self.controller.play_music()
                    results.append("Playing music")
                elif action == "create_folder":
                    self.controller.create_folder(params)
                    results.append(f"Created folder {params}")
                elif action == "open_reels":
                    self.controller.open_reels()
                    results.append("Opened reels")
                elif action == "click_text":
                    success = self.vision.click_text(params)
                    if success:
                        results.append(f"Clicked on {params}")
                    else:
                        results.append(f"Could not find {params} on screen")
                        self.speak(f"Sorry, I couldn't find {params}")
                elif action == "write_document":
                    self.controller.write_document(params)
                    results.append(f"Wrote {params}")
                elif action == "close_app":
                    self.controller.close_app()
                    results.append("Closed active window")
                else:
                    results.append(f"Unknown action: {action}")
                
                time.sleep(0.5) # Reduced delay for better performance
            except Exception as e:
                error_msg = f"Error executing {action}: {str(e)}"
                results.append(error_msg)
                self.speak(f"There was an error with {action}")
        
        self.speak("All tasks completed.")
        return results
