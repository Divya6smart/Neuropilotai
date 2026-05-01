from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys
import asyncio
from typing import List

import sys

# Add the current directory to sys.path to handle imports correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import our modules
from backend.vision.vision_engine import VisionEngine
from backend.system_control.controller import SystemController
from backend.command_parser.parser import CommandParser
from backend.executor.executor import TaskExecutor

app = FastAPI(title="VoxOS - Voice + Vision PC Controller")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression for faster asset delivery
app.add_middleware(GZipMiddleware, minimum_size=1000)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Initialize engines
vision = VisionEngine()
controller = SystemController()
parser = CommandParser()
executor = TaskExecutor(controller, vision)

class VoiceCommand(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(current_dir, "frontend", "index.html")
    with open(index_path, "r") as f:
        return f.read()

@app.post("/voice-command")
async def process_voice_command(command: VoiceCommand, background_tasks: BackgroundTasks = None):
    text = command.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty command")
    
    await manager.broadcast({"type": "status", "message": "Parsing command..."})
    
    commands = parser.split_commands(text)
    tasks = [parser.parse(cmd) for cmd in commands]
    
    # Broadcast tasks to frontend via WebSocket
    await manager.broadcast({"type": "tasks", "data": tasks})
    
    # Execute in a separate thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, executor.execute_tasks, tasks)
    
    for res in results:
        await manager.broadcast({"type": "execution", "message": res})
    
    return {
        "status": "success",
        "raw_text": text,
        "parsed_tasks": tasks,
        "execution_results": results
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/status")
async def get_status():
    return {
        "authenticated": True,
        "online": True,
        "last_summary": "System ready",
        "workflows": ["open_app", "vision_click", "media_control"]
    }

# Serve static files from the frontend directory
static_path = os.path.join(current_dir, "frontend")
app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
