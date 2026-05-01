"""Critic agent — evaluates execution results and suggests recovery strategies."""
import logging

logger = logging.getLogger(__name__)


class CriticAgent:
    def __init__(self):
        self.failure_counts: dict[str, int] = {}  # action_type -> count

    def evaluate(self, step: dict, success: bool,
                 final_state_image: str = None) -> dict:
        """Evaluate step outcome. Returns critique with risk score and recovery plan."""
        action_type = step.get("action_type", "unknown")

        if success:
            self.failure_counts[action_type] = 0
            return {
                "status": "passed",
                "risk_score": 0.0,
                "feedback": f"Action '{action_type}' succeeded.",
            }

        # Track consecutive failures for escalation
        self.failure_counts[action_type] = self.failure_counts.get(action_type, 0) + 1
        count = self.failure_counts[action_type]

        logger.warning(f"Critic: '{action_type}' failed ({count} consecutive)")

        # Escalating recovery strategies
        if count >= 3:
            return {
                "status": "failed",
                "risk_score": 1.0,
                "feedback": f"'{action_type}' failed {count}x — recommending abort.",
                "recommendation": "abort",
            }
        elif count == 2:
            return {
                "status": "failed",
                "risk_score": 0.8,
                "feedback": "Repeated failure — trying screenshot re-analysis.",
                "alternate_strategy": {"action_type": "wait", "params": {"duration": 3}},
            }
        else:
            return {
                "status": "failed",
                "risk_score": 0.5,
                "feedback": "First failure — retrying with delay.",
                "alternate_strategy": {"action_type": "wait", "params": {"duration": 2}},
            }


critic_agent = CriticAgent()
