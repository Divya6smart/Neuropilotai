"""Tests for agent modules: memory, planner, critic, brain."""
import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
config.validate()


class TestMemory:
    def setup_method(self):
        from agent.memory import MemorySystem
        self.tmpfile = os.path.join(config.DATA_DIR, "_test_memory.json")
        self.mem = MemorySystem(memory_file=self.tmpfile)

    def teardown_method(self):
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)

    def test_add_and_retrieve_action(self):
        self.mem.add_action("test task", {"action_type": "click"}, True)
        history = self.mem.get_history(10)
        assert len(history) == 1
        assert history[0]["task"] == "test task"
        assert history[0]["success"] is True

    def test_history_limit(self):
        for i in range(10):
            self.mem.add_action(f"task_{i}", {"action_type": "type"}, True)
        assert len(self.mem.get_history(5)) == 5

    def test_add_and_find_pattern(self):
        self.mem.add_pattern("open notepad", [{"action_type": "hotkey"}])
        result = self.mem.find_pattern("open notepad")
        assert result is not None
        assert result[0]["action_type"] == "hotkey"

    def test_find_pattern_missing(self):
        assert self.mem.find_pattern("nonexistent") is None

    def test_pattern_update(self):
        self.mem.add_pattern("ctx", [{"a": 1}])
        self.mem.add_pattern("ctx", [{"a": 2}])
        result = self.mem.find_pattern("ctx")
        assert result[0]["a"] == 2

    def test_corrupted_file_recovery(self):
        with open(self.tmpfile, "w") as f:
            f.write("not json{{{")
        data = self.mem._load()
        assert "history" in data


class TestPlanner:
    def test_notepad_plan(self):
        from agent.planner import planner_agent
        plan = planner_agent.plan_task("open notepad and type hello")
        assert len(plan) > 0
        action_types = [s["action_type"] for s in plan]
        assert "type" in action_types

    def test_youtube_plan(self):
        from agent.planner import planner_agent
        plan = planner_agent.plan_task("open youtube")
        assert len(plan) > 0

    def test_unknown_task_returns_log(self):
        from agent.planner import planner_agent
        plan = planner_agent.plan_task("do something random xyz")
        assert plan[0]["action_type"] == "log"


class TestCritic:
    def test_success_evaluation(self):
        from agent.critic import critic_agent
        result = critic_agent.evaluate({"action_type": "click"}, True)
        assert result["status"] == "passed"
        assert result["risk_score"] == 0.0

    def test_failure_provides_alternate(self):
        from agent.critic import CriticAgent
        critic = CriticAgent()
        result = critic.evaluate({"action_type": "test_action"}, False)
        assert result["status"] == "failed"
        assert "alternate_strategy" in result

    def test_repeated_failure_escalates(self):
        from agent.critic import CriticAgent
        critic = CriticAgent()
        for _ in range(3):
            result = critic.evaluate({"action_type": "bad_action"}, False)
        assert result.get("recommendation") == "abort"
        assert result["risk_score"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
