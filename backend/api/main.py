from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.orchestrator.main import orchestrator
from backend.agents.devops.agents import ReviewAgent, SecurityAgent
from backend.agents.system.agent import SystemAgent
from backend.memory.vector_store import memory
import asyncio
import os

app = FastAPI(title="NeuroPilot AI - Elite DevOps Orchestrator")

# Path to dashboard
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DASHBOARD_PATH = os.path.join(BASE_DIR, "frontend", "dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    index_path = os.path.join(DASHBOARD_PATH, "index.html")
    with open(index_path, "r") as f:
        return f.read()

# Register agents
orchestrator.register_agent("ReviewAgent", ReviewAgent())
orchestrator.register_agent("SecurityAgent", SecurityAgent())
orchestrator.register_agent("SystemAgent", SystemAgent())

class TaskRequest(BaseModel):
    task: str

@app.post("/execute")
async def execute_task(request: TaskRequest):
    # Store in memory for context
    memory.store(request.task, {"type": "user_request"})
    
    # Run Orchestrator
    results = await orchestrator.plan_and_execute(request.task)
    return {"status": "success", "results": [r.model_dump() for r in results]}

@app.websocket("/ws/events")
async def event_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Heartbeat or event streaming logic
            await asyncio.sleep(1)
            await websocket.send_json({"status": "healthy", "agent_count": len(orchestrator.agents)})
    except WebSocketDisconnect:
        pass
