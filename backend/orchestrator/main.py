import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from backend.agents.base import AgentResponse

class Orchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.agents = {}
        self.memory = None # To be implemented in Phase 3

    def register_agent(self, name: str, agent_instance):
        self.agents[name] = agent_instance

    async def plan_and_execute(self, task_description: str) -> List[AgentResponse]:
        # 1. Planning Phase (LLM)
        prompt = f"""
        You are the NeuroPilot AI Orchestrator. 
        Available Agents: {list(self.agents.keys())}
        
        Task: {task_description}
        
        Decide the sequence of agents to run. Return ONLY a JSON list of agent names.
        Example: ["ReviewAgent", "SecurityAgent"]
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        
        plan = json.loads(response.choices[0].message.content)
        print(f"[Orchestrator] Plan: {plan}")
        
        # 2. Execution Phase
        results = []
        for agent_name in plan:
            if agent_name in self.agents:
                print(f"[Orchestrator] Running {agent_name}...")
                result = await self.agents[agent_name].run({"task": task_description})
                results.append(result)
            else:
                print(f"[Orchestrator] Warning: Agent {agent_name} not found.")
        
        return results

orchestrator = Orchestrator()
