from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from agent.brain import brain_system
from security.biometrics import security_system

app = FastAPI(title="NeuroPilot AI API", version="1.0.0")

class TaskRequest(BaseModel):
    instruction: str
    
class AuthRequest(BaseModel):
    user_id: str
    auth_token: str

@app.get("/")
def read_root():
    return {"status": "NeuroPilot AI is running"}

@app.post("/auth/face")
def auth_face():
    # In a real scenario, an image is uploaded and processed
    # Here we mock it
    if security_system.verify_face("data/screenshots/latest.png"):
        return {"status": "Authenticated", "risk_level": "low"}
    raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/execute")
def execute_task(req: TaskRequest, background_tasks: BackgroundTasks):
    if brain_system.is_running:
        return {"status": "Busy", "message": "Agent is currently executing a task."}
        
    background_tasks.add_task(brain_system.start_task, req.instruction)
    return {"status": "Started", "task": req.instruction}

@app.post("/stop")
def stop_task():
    brain_system.stop_task()
    return {"status": "Stopped"}

@app.get("/status")
def get_status():
    return {
        "is_running": brain_system.is_running,
        "current_task": brain_system.current_task
    }
