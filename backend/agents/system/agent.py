from backend.agents.base import BaseAgent, AgentResponse
from backend.agents.system.executor.executor import TaskExecutor
from backend.agents.system.system_control.controller import SystemController
from backend.agents.system.vision.vision_engine import VisionEngine
from backend.agents.system.command_parser.parser import CommandParser
from typing import Dict, Any

class SystemAgent(BaseAgent):
    def __init__(self):
        super().__init__("SystemAgent")
        self.controller = SystemController()
        self.vision = VisionEngine()
        self.parser = CommandParser()
        self.executor = TaskExecutor(self.controller, self.vision)

    async def run(self, input_data: Dict[str, Any]) -> AgentResponse:
        task = input_data.get("task", "")
        print(f"[SystemAgent] Running task: {task}")
        
        # Use existing parsing and execution logic
        commands = self.parser.split_commands(task)
        print(f"[SystemAgent] Split into {len(commands)} commands")
        
        tasks = [self.parser.parse(cmd) for cmd in commands]
        print(f"[SystemAgent] Parsed tasks: {tasks}")
        
        results = self.executor.execute_tasks(tasks)
        print(f"[SystemAgent] Execution results: {results}")
        
        return AgentResponse(
            agent_name=self.name,
            status="Success",
            output=results,
            metadata={"parsed_tasks": tasks}
        )
