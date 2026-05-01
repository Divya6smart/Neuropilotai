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
        # 1. Planning Phase (LLM with Local Fallback)
        plan = []
        try:
            # Check for placeholder key
            if "replace_" in str(os.getenv("OPENAI_API_KEY")):
                raise ValueError("Placeholder API Key detected")

            prompt = f"""
            You are the NeuroPilot AI Orchestrator. 
            Available Agents: ReviewAgent, SecurityAgent, SystemAgent.
            Task: {task_description}
            Return ONLY a JSON list of agent names.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": prompt}]
            )
            raw_content = response.choices[0].message.content.strip()
            # Clean JSON... (simplified for now as I have the logic above)
            if "SystemAgent" in raw_content: plan.append("SystemAgent")
            if "SecurityAgent" in raw_content: plan.append("SecurityAgent")
            if "ReviewAgent" in raw_content: plan.append("ReviewAgent")
            
        except Exception as e:
            print(f"[Orchestrator] Using Local Fallback Planner due to: {e}")
            # Intelligent local fallback
            task_lower = task_description.lower()
            if any(x in task_lower for x in ["open", "search", "click", "launch", "write", "close"]):
                plan = ["SystemAgent"]
            if any(x in task_lower for x in ["security", "audit", "vulnerability"]):
                plan.append("SecurityAgent")
            if any(x in task_lower for x in ["review", "check", "code"]):
                plan.append("ReviewAgent")

        print(f"[Orchestrator] Planned Agents: {plan}")
        
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
