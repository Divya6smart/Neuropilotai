import threading
import time
from agent.planner import planner_agent
from agent.executor import executor_agent
from agent.critic import critic_agent
from agent.memory import memory_system
from utils.screen import screen_manager

class Brain:
    def __init__(self):
        self.is_running = False
        self.current_task = None
        
    def start_task(self, instruction: str):
        self.current_task = instruction
        self.is_running = True
        
        # Parallel Task Execution using threading
        thread = threading.Thread(target=self._run_loop, args=(instruction,))
        thread.start()
        
    def stop_task(self):
        self.is_running = False

    def _run_loop(self, instruction: str):
        print(f"Brain: Starting autonomous loop for '{instruction}'")
        
        # Step 1: Predict or Plan
        # Check memory for patterns
        prediction = memory_system.find_pattern(instruction)
        if prediction:
            print(f"Predictive Engine: Found matching pattern, executing predicted plan.")
            plan = prediction
        else:
            plan = planner_agent.plan_task(instruction)
            
        # Step 2: Execution Loop
        for step in plan:
            if not self.is_running:
                print("Brain: Task halted by user.")
                break
                
            # Simulate before action (risk estimation)
            if step.get("action_type") == "delete":
                print("Brain WARNING: High risk action detected. Simulating outcome...")
                
            # Execute
            success = executor_agent.execute_step(step)
            
            # Critic Evaluate
            img_path = screen_manager.capture_screen()
            evaluation = critic_agent.evaluate(step, success, img_path)
            
            # Memory Storage
            memory_system.add_action(instruction, step, success)
            
            # Self-Healing
            if evaluation["status"] == "failed" and "alternate_strategy" in evaluation:
                print("Brain: Applying self-healing strategy.")
                executor_agent.execute_step(evaluation["alternate_strategy"])
                
            time.sleep(1) # Prevent too fast execution

        print("Brain: Task complete.")
        self.is_running = False

brain_system = Brain()
