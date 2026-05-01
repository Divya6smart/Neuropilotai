import time
import psutil
import threading
from collections import deque

class PerformanceMonitor:
    def __init__(self, history_size=100):
        self.latency_history = deque(maxlen=history_size)
        self.cpu_usage = deque(maxlen=history_size)
        self.memory_usage = deque(maxlen=history_size)
        self.last_api_call = None
        
        # Start background collector
        self._running = True
        self._thread = threading.Thread(target=self._collect_stats, daemon=True)
        self._thread.start()

    def _collect_stats(self):
        while self._running:
            self.cpu_usage.append(psutil.cpu_percent())
            self.memory_usage.append(psutil.virtual_memory().percent)
            time.sleep(2)

    def record_latency(self, latency_ms):
        self.latency_history.append(latency_ms)

    def get_metrics(self):
        avg_latency = sum(self.latency_history) / len(self.latency_history) if self.latency_history else 0
        return {
            "avg_latency_ms": round(avg_latency, 2),
            "cpu_percent": self.cpu_usage[-1] if self.cpu_usage else 0,
            "memory_percent": self.memory_usage[-1] if self.memory_usage else 0,
            "status": "Healthy",
            "uptime": "Active"
        }

monitor = PerformanceMonitor()
