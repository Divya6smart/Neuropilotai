from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Any, List

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    output: Any
    next_steps: List[str] = []
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> AgentResponse:
        pass
