class PredictionEngine:
    def __init__(self):
        # Basic Markov chain or rule-based predictor
        self.history = []
        self.rules = {
            "open chrome": ["search google", "check email", "open youtube"],
            "open terminal": ["run build", "git status", "npm start"],
            "open notepad": ["write notes", "save file"],
            "play music": ["volume up", "open reels"]
        }

    def record_action(self, action_text):
        self.history.append(action_text.lower())
        if len(self.history) > 10:
            self.history.pop(0)

    def predict_next(self, current_action):
        current_action = current_action.lower()
        predictions = []
        
        # Check direct rules
        for key, value in self.rules.items():
            if key in current_action:
                predictions.extend(value)
        
        return list(set(predictions))[:3]

predictor = PredictionEngine()
