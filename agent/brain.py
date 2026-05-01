"""Thread-safe brain with WebSocket broadcast and self-healing loop."""
import threading
import time
import logging
import asyncio
from agent.planner import planner_agent
from agent.executor import executor_agent
from agent.critic import critic_agent
from agent.memory import memory_system
from utils.screen import screen_manager

logger = logging.getLogger(__name__)


class Brain:
    def __init__(self):
        self._lock = threading.Lock()
        self._is_running = False
        self._current_task = None
        self._ws_clients: list = []  # WebSocket connections for real-time updates
        self._event_log: list = []

    # ── Thread-safe properties ────────────────────────────
    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._is_running

    @is_running.setter
    def is_running(self, val: bool):
        with self._lock:
            self._is_running = val

    @property
    def current_task(self):
        with self._lock:
            return self._current_task

    @current_task.setter
    def current_task(self, val):
        with self._lock:
            self._current_task = val

    # ── WebSocket management ──────────────────────────────
    def register_ws(self, ws):
        self._ws_clients.append(ws)

    def unregister_ws(self, ws):
        if ws in self._ws_clients:
            self._ws_clients.remove(ws)

    async def _broadcast(self, message: dict):
        """Send real-time updates to all connected WebSocket clients."""
        import json
        dead = []
        for ws in self._ws_clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._ws_clients.remove(ws)

    def _sync_broadcast(self, message: dict):
        """Broadcast from a sync context (worker thread)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(self._broadcast(message), loop)
        except RuntimeError:
            pass  # no event loop — skip

    # ── Task execution ────────────────────────────────────
    def start_task(self, instruction: str):
        self.current_task = instruction
        self.is_running = True
        thread = threading.Thread(target=self._run_loop, args=(instruction,),
                                  daemon=True)
        thread.start()

    def stop_task(self):
        logger.info("Brain: Task stop requested")
        self.is_running = False

    def _run_loop(self, instruction: str):
        logger.info(f"Brain: Starting '{instruction}'")
        self._sync_broadcast({"event": "task_started", "task": instruction})

        # Predictive: check memory for known patterns
        prediction = memory_system.find_pattern(instruction)
        if prediction:
            logger.info("Predictive engine: using cached plan")
            plan = prediction
        else:
            plan = planner_agent.plan_task(instruction)

        for i, step in enumerate(plan):
            if not self.is_running:
                logger.info("Brain: Halted by user")
                self._sync_broadcast({"event": "task_halted", "step": i})
                break

            # Safety gate: warn on destructive actions
            if step.get("action_type") == "delete":
                logger.warning("HIGH RISK action detected — simulating first")
                self._sync_broadcast({"event": "risk_warning", "step": step})

            self._sync_broadcast({"event": "step_start", "step_index": i, "step": step})

            success = executor_agent.execute_step(step)

            # Critic evaluation
            img_path = screen_manager.capture_screen()
            evaluation = critic_agent.evaluate(step, success, img_path)

            memory_system.add_action(instruction, step, success)

            # Self-healing
            if evaluation["status"] == "failed":
                if evaluation.get("recommendation") == "abort":
                    logger.error("Critic recommends abort — stopping")
                    self._sync_broadcast({"event": "task_aborted", "reason": evaluation["feedback"]})
                    break
                if "alternate_strategy" in evaluation:
                    logger.info("Self-healing: executing recovery strategy")
                    executor_agent.execute_step(evaluation["alternate_strategy"])

            self._sync_broadcast({
                "event": "step_complete", "step_index": i,
                "success": success, "risk_score": evaluation.get("risk_score", 0),
            })
            time.sleep(0.5)

        logger.info("Brain: Task loop finished")
        self.is_running = False
        self._sync_broadcast({"event": "task_complete", "task": instruction})


brain_system = Brain()
