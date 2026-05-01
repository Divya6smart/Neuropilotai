"""Continuous authentication — behavior monitoring & anomaly detection."""
import time
import threading
import logging
import statistics
from collections import deque

logger = logging.getLogger(__name__)


class BehaviorProfile:
    """Tracks per-user typing/mouse behavior for anomaly detection."""

    def __init__(self, window_size: int = 100):
        self.typing_intervals = deque(maxlen=window_size)
        self.mouse_speeds = deque(maxlen=window_size)
        self.action_timestamps = deque(maxlen=window_size)
        self._baseline_typing = None
        self._baseline_mouse = None
        self._lock = threading.Lock()

    def record_keystroke(self, timestamp: float):
        with self._lock:
            if self.action_timestamps:
                interval = timestamp - self.action_timestamps[-1]
                if interval < 5.0:
                    self.typing_intervals.append(interval)
            self.action_timestamps.append(timestamp)

    def record_mouse_movement(self, speed: float):
        with self._lock:
            self.mouse_speeds.append(speed)

    def set_baseline(self):
        with self._lock:
            if len(self.typing_intervals) >= 10:
                vals = list(self.typing_intervals)
                self._baseline_typing = {
                    "mean": statistics.mean(vals),
                    "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.1,
                }
            if len(self.mouse_speeds) >= 10:
                vals = list(self.mouse_speeds)
                self._baseline_mouse = {
                    "mean": statistics.mean(vals),
                    "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.1,
                }


class ContinuousAuthenticator:
    """Monitors user behavior and triggers re-auth when confidence drops."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.profiles: dict[str, BehaviorProfile] = {}
        self.confidence_scores: dict[str, float] = {}
        self._lock = threading.Lock()
        self._reauth_callbacks = []
        logger.info(f"ContinuousAuth initialized (threshold={threshold})")

    def register_user(self, user_id: str):
        with self._lock:
            if user_id not in self.profiles:
                self.profiles[user_id] = BehaviorProfile()
                self.confidence_scores[user_id] = 1.0

    def record_activity(self, user_id: str, activity_type: str, data: dict):
        with self._lock:
            if user_id not in self.profiles:
                self.profiles[user_id] = BehaviorProfile()
                self.confidence_scores[user_id] = 1.0
        profile = self.profiles[user_id]
        if activity_type == "keystroke":
            profile.record_keystroke(data.get("timestamp", time.time()))
        elif activity_type == "mouse_move":
            profile.record_mouse_movement(data.get("speed", 0.0))

    def calculate_confidence(self, user_id: str) -> float:
        with self._lock:
            if user_id not in self.profiles:
                return 0.0
            profile = self.profiles[user_id]

        scores = []
        with profile._lock:
            if profile._baseline_typing and len(profile.typing_intervals) >= 5:
                current_mean = statistics.mean(list(profile.typing_intervals)[-20:])
                bl = profile._baseline_typing
                if bl["stdev"] > 0:
                    z = abs(current_mean - bl["mean"]) / bl["stdev"]
                    scores.append(max(0.0, 1.0 - (z / 3.0)))

            if profile._baseline_mouse and len(profile.mouse_speeds) >= 5:
                current_mean = statistics.mean(list(profile.mouse_speeds)[-20:])
                bl = profile._baseline_mouse
                if bl["stdev"] > 0:
                    z = abs(current_mean - bl["mean"]) / bl["stdev"]
                    scores.append(max(0.0, 1.0 - (z / 3.0)))

        if not scores:
            return 1.0  # not enough data yet

        confidence = statistics.mean(scores)
        with self._lock:
            self.confidence_scores[user_id] = confidence

        if confidence < self.threshold:
            logger.warning(f"Confidence {confidence:.2f} < threshold for {user_id}")
            self._trigger_reauth(user_id)

        return confidence

    def on_reauth_required(self, callback):
        self._reauth_callbacks.append(callback)

    def _trigger_reauth(self, user_id: str):
        logger.warning(f"Re-authentication triggered for {user_id}")
        for cb in self._reauth_callbacks:
            try:
                cb(user_id)
            except Exception as e:
                logger.error(f"Re-auth callback error: {e}")

    def get_risk_score(self, user_id: str) -> float:
        with self._lock:
            c = self.confidence_scores.get(user_id, 1.0)
        return round(1.0 - c, 3)
